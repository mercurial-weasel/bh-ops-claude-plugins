"""
Enhanced PDF Loader Script with Image Extraction

This script loads all PDFs from the ./my_pdfs directory,
extracts both text content AND images, performs OCR on images,
generates AI descriptions of images, and creates a unified
FAISS index containing all content for comprehensive search.
"""

import os
import faiss
import numpy as np
import pickle
import re
import nltk
import fitz  # PyMuPDF
import cv2
import base64
from io import BytesIO
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from langchain.schema import Document

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading NLTK punkt tokenizer...")
    nltk.download('punkt')

# Ollama configuration for image descriptions
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"

def extract_chapter_section_info(text):
    """
    Extract chapter and section information from text using regex patterns.
    
    Args:
        text (str): Text content to analyze
        
    Returns:
        dict: Dictionary containing chapter and section information
    """
    chapter_info = {
        'chapter_title': None,
        'chapter_number': None,
        'section_number': None,
        'section_title': None,
        'clause_number': None,
        'clause_title': None
    }
    
    # Common patterns for building standards and regulations
    patterns = {
        'chapter': [
            r'(?i)^chapter\s+(\d+(?:\.\d+)*)\s*[-–—]?\s*(.+?)(?:\n|$)',
            r'(?i)^part\s+(\d+(?:\.\d+)*)\s*[-–—]?\s*(.+?)(?:\n|$)',
            r'(?i)^section\s+([A-Z]|\d+)\s*[-–—]?\s*(.+?)(?:\n|$)',
            r'^([A-Z][A-Z\s]+)$'  # All caps headings
        ],
        'section': [
            r'(?i)^(\d+(?:\.\d+)*)\s+(.+?)(?:\n|$)',
            r'(?i)^section\s+(\d+(?:\.\d+)*)\s*[-–—]?\s*(.+?)(?:\n|$)',
            r'(?i)^(\d+(?:\.\d+)*)\s*[-–—]\s*(.+?)(?:\n|$)'
        ],
        'clause': [
            r'(?i)^(\d+(?:\.\d+){2,})\s+(.+?)(?:\n|$)',
            r'(?i)^clause\s+(\d+(?:\.\d+)*)\s*[-–—]?\s*(.+?)(?:\n|$)'
        ]
    }
    
    lines = text.split('\n')
    
    for line in lines[:10]:  # Check first 10 lines for headers
        line = line.strip()
        if not line:
            continue
            
        # Check for chapter patterns
        for pattern in patterns['chapter']:
            match = re.match(pattern, line)
            if match:
                if len(match.groups()) >= 2:
                    chapter_info['chapter_number'] = match.group(1)
                    chapter_info['chapter_title'] = match.group(2).strip()
                elif len(match.groups()) == 1:
                    chapter_info['chapter_title'] = match.group(1).strip()
                break
        
        # Check for section patterns
        for pattern in patterns['section']:
            match = re.match(pattern, line)
            if match and len(match.groups()) >= 2:
                chapter_info['section_number'] = match.group(1)
                chapter_info['section_title'] = match.group(2).strip()
                break
        
        # Check for clause patterns
        for pattern in patterns['clause']:
            match = re.match(pattern, line)
            if match and len(match.groups()) >= 2:
                chapter_info['clause_number'] = match.group(1)
                chapter_info['clause_title'] = match.group(2).strip()
                break
    
    return chapter_info

def extract_complete_sentences(text, target_position=None, max_sentences=3):
    """
    Extract complete sentences around a target position or from the beginning.
    
    Args:
        text (str): Text to extract sentences from
        target_position (int): Position in text to center extraction around
        max_sentences (int): Maximum number of sentences to extract
        
    Returns:
        str: Complete sentences
    """
    try:
        sentences = nltk.sent_tokenize(text)
        
        if not sentences:
            return text[:300] + "..." if len(text) > 300 else text
        
        if target_position is None:
            # Return first few sentences
            return ' '.join(sentences[:max_sentences])
        
        # Find sentence containing target position
        current_pos = 0
        target_sentence_idx = 0
        
        for i, sentence in enumerate(sentences):
            if current_pos <= target_position <= current_pos + len(sentence):
                target_sentence_idx = i
                break
            current_pos += len(sentence) + 1  # +1 for space
        
        # Extract sentences around target
        start_idx = max(0, target_sentence_idx - max_sentences // 2)
        end_idx = min(len(sentences), start_idx + max_sentences)
        
        return ' '.join(sentences[start_idx:end_idx])
    
    except Exception as e:
        print(f"Error in sentence extraction: {e}")
        return text[:300] + "..." if len(text) > 300 else text

def extract_images_from_pdf(pdf_path, output_dir):
    """
    Extract all images from a PDF file using PyMuPDF.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory to save extracted images
        
    Returns:
        list: List of dictionaries containing image information
    """
    images_info = []
    
    try:
        # Create output directory for this PDF
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        pdf_output_dir = os.path.join(output_dir, pdf_name)
        os.makedirs(pdf_output_dir, exist_ok=True)
        
        # Open PDF with PyMuPDF
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Get images on this page
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Get image data
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    # Skip if image is too small (likely decorative)
                    if pix.width < 50 or pix.height < 50:
                        pix = None
                        continue
                    
                    # Convert to PIL Image
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = pix.tobytes("png")
                        img_pil = Image.open(BytesIO(img_data))
                    else:  # CMYK: convert to RGB first
                        pix1 = fitz.Pixmap(fitz.csRGB, pix)
                        img_data = pix1.tobytes("png")
                        img_pil = Image.open(BytesIO(img_data))
                        pix1 = None
                    
                    # Save image
                    img_filename = f"page_{page_num + 1}_img_{img_index + 1}.png"
                    img_path = os.path.join(pdf_output_dir, img_filename)
                    img_pil.save(img_path)
                    
                    # Store image information
                    images_info.append({
                        'path': img_path,
                        'page': page_num,
                        'index': img_index,
                        'width': pix.width,
                        'height': pix.height,
                        'filename': img_filename,
                        'source_pdf': pdf_path
                    })
                    
                    pix = None
                    
                except Exception as e:
                    print(f"Error extracting image {img_index} from page {page_num}: {e}")
                    continue
        
        doc.close()
        print(f"Extracted {len(images_info)} images from {pdf_name}")
        
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
    
    return images_info

def perform_ocr_on_image(image_path):
    """
    Perform OCR on an image to extract text.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Extracted text from the image
    """
    try:
        # Load image
        image = cv2.imread(image_path)
        
        # Preprocess image for better OCR
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get better text recognition
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Perform OCR
        text = pytesseract.image_to_string(thresh, config='--psm 6')
        
        # Clean up text
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text if text else ""
        
    except Exception as e:
        print(f"Error performing OCR on {image_path}: {e}")
        return ""

def generate_image_description(image_path):
    """
    Generate an AI description of an image using Ollama.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: AI-generated description of the image
    """
    try:
        # For now, we'll create a basic description based on image properties
        # In the future, this could use Ollama's vision capabilities
        
        image = Image.open(image_path)
        width, height = image.size
        
        # Basic classification based on aspect ratio and size
        aspect_ratio = width / height
        
        if aspect_ratio > 2:
            image_type = "horizontal diagram or chart"
        elif aspect_ratio < 0.5:
            image_type = "vertical diagram or chart"
        elif 0.8 <= aspect_ratio <= 1.2:
            image_type = "square diagram, chart, or technical drawing"
        else:
            image_type = "technical diagram or illustration"
        
        # Size classification
        if width * height > 500000:
            size_desc = "large detailed"
        elif width * height > 100000:
            size_desc = "medium-sized"
        else:
            size_desc = "small"
        
        description = f"A {size_desc} {image_type} ({width}x{height} pixels) from a building standards document. This image likely contains technical information, specifications, diagrams, or regulatory details relevant to construction and building codes."
        
        return description
        
    except Exception as e:
        print(f"Error generating description for {image_path}: {e}")
        return "Technical image from building standards document"

def process_images_for_page(images_info, page_num):
    """
    Process all images for a specific page, performing OCR and generating descriptions.
    
    Args:
        images_info (list): List of image information dictionaries
        page_num (int): Page number to process
        
    Returns:
        dict: Combined image content for the page
    """
    page_images = [img for img in images_info if img['page'] == page_num]
    
    if not page_images:
        return None
    
    combined_content = {
        'image_descriptions': [],
        'ocr_text': [],
        'image_paths': [],
        'image_count': len(page_images)
    }
    
    for img_info in page_images:
        # Perform OCR
        ocr_text = perform_ocr_on_image(img_info['path'])
        if ocr_text:
            combined_content['ocr_text'].append(ocr_text)
        
        # Generate description
        description = generate_image_description(img_info['path'])
        combined_content['image_descriptions'].append(description)
        
        # Store image path
        combined_content['image_paths'].append(img_info['path'])
    
    return combined_content

class EnhancedSentenceAwareTextSplitter:
    """
    Enhanced text splitter that preserves sentence boundaries and includes image content.
    """
    
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_documents_with_images(self, documents, all_images_info):
        """
        Split documents while preserving sentence boundaries and adding image content.
        
        Args:
            documents (list): List of documents to split
            all_images_info (dict): Dictionary mapping PDF paths to image information
            
        Returns:
            list: List of split documents with enhanced metadata including images
        """
        split_docs = []
        
        for doc in documents:
            # Extract chapter/section info from the document
            chapter_info = extract_chapter_section_info(doc.page_content)
            
            # Get images for this document and page
            source_path = doc.metadata.get('source_path', '')
            page_num = doc.metadata.get('page', 0)
            
            images_info = all_images_info.get(source_path, [])
            page_image_content = process_images_for_page(images_info, page_num)
            
            # Split into sentences first
            try:
                sentences = nltk.sent_tokenize(doc.page_content)
            except Exception as e:
                print(f"Error tokenizing sentences: {e}")
                sentences = [doc.page_content]
            
            if not sentences:
                continue
            
            # Group sentences into chunks
            current_chunk = ""
            current_sentences = []
            
            for sentence in sentences:
                # Check if adding this sentence would exceed chunk size
                if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                    # Create a chunk from current sentences
                    chunk_doc = self._create_enhanced_chunk_document(
                        doc, current_chunk, current_sentences, chapter_info, page_image_content
                    )
                    split_docs.append(chunk_doc)
                    
                    # Start new chunk with overlap
                    overlap_sentences = current_sentences[-2:] if len(current_sentences) > 2 else current_sentences
                    current_chunk = ' '.join(overlap_sentences)
                    current_sentences = overlap_sentences.copy()
                
                current_chunk += (" " if current_chunk else "") + sentence
                current_sentences.append(sentence)
            
            # Add the final chunk if it has content
            if current_chunk.strip():
                chunk_doc = self._create_enhanced_chunk_document(
                    doc, current_chunk, current_sentences, chapter_info, page_image_content
                )
                split_docs.append(chunk_doc)
        
        return split_docs
    
    def _create_enhanced_chunk_document(self, original_doc, chunk_text, sentences, chapter_info, page_image_content):
        """
        Create a new document chunk with enhanced metadata including image content.
        
        Args:
            original_doc: Original document
            chunk_text (str): Text content of the chunk
            sentences (list): List of sentences in the chunk
            chapter_info (dict): Chapter/section information
            page_image_content (dict): Image content for this page
            
        Returns:
            Document: New document with enhanced metadata including images
        """
        # Copy original metadata
        new_metadata = original_doc.metadata.copy()
        
        # Add chapter/section information
        new_metadata.update(chapter_info)
        
        # Add sentence context
        new_metadata['sentence_count'] = len(sentences)
        new_metadata['complete_sentences'] = extract_complete_sentences(chunk_text, max_sentences=3)
        
        # Add chunk information
        new_metadata['chunk_length'] = len(chunk_text)
        
        # Add image content if available
        if page_image_content:
            new_metadata['has_images'] = True
            new_metadata['image_count'] = page_image_content['image_count']
            new_metadata['image_paths'] = page_image_content['image_paths']
            new_metadata['image_descriptions'] = page_image_content['image_descriptions']
            new_metadata['ocr_text'] = page_image_content['ocr_text']
            
            # Combine text with image content for embedding
            enhanced_content = chunk_text
            
            # Add image descriptions
            if page_image_content['image_descriptions']:
                enhanced_content += "\n\nIMAGE CONTENT:\n"
                for i, desc in enumerate(page_image_content['image_descriptions']):
                    enhanced_content += f"Image {i+1}: {desc}\n"
            
            # Add OCR text
            if page_image_content['ocr_text']:
                enhanced_content += "\nTEXT FROM IMAGES:\n"
                for ocr_text in page_image_content['ocr_text']:
                    if ocr_text.strip():
                        enhanced_content += f"{ocr_text}\n"
            
            return Document(page_content=enhanced_content, metadata=new_metadata)
        else:
            new_metadata['has_images'] = False
            new_metadata['image_count'] = 0
            return Document(page_content=chunk_text, metadata=new_metadata)

def load_pdfs_with_enhanced_processing():
    """
    Load all PDFs from the ./my_pdfs directory and extract both text and images.
    
    Returns:
        tuple: (documents, all_images_info)
    """
    print("Starting enhanced PDF loading process with image extraction...")
    
    # Check if directory exists
    pdf_dir = "./my_pdfs"
    if not os.path.exists(pdf_dir):
        print(f"Directory {pdf_dir} does not exist. Creating it...")
        os.makedirs(pdf_dir)
        print(f"Please place your PDF files in the {pdf_dir} directory and run this script again.")
        return [], {}
    
    # Check if directory contains any PDF files (recursively)
    pdf_files = []
    for root, dirs, files in os.walk(pdf_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir} or its subdirectories. Please add some PDF files and run this script again.")
        return [], {}
    
    print(f"Found {len(pdf_files)} PDF files in {pdf_dir} and its subdirectories.")
    
    # Create images output directory
    images_output_dir = "./extracted_images"
    os.makedirs(images_output_dir, exist_ok=True)
    
    # Load PDFs and extract images
    documents = []
    all_images_info = {}
    
    for pdf_path in pdf_files:
        pdf_file = os.path.basename(pdf_path)
        print(f"Processing {pdf_file}...")
        
        try:
            # Extract text using PyPDFLoader
            loader = PyPDFLoader(pdf_path)
            pdf_documents = loader.load()
            
            # Extract images from the same PDF
            images_info = extract_images_from_pdf(pdf_path, images_output_dir)
            all_images_info[pdf_path] = images_info
            
            # Add source metadata to each document
            for doc in pdf_documents:
                if not hasattr(doc, 'metadata'):
                    doc.metadata = {}
                doc.metadata['source_file'] = pdf_file
                doc.metadata['source_path'] = pdf_path
                relative_path = os.path.relpath(pdf_path, pdf_dir)
                doc.metadata['relative_path'] = relative_path
            
            print(f"Successfully loaded {pdf_file} with {len(pdf_documents)} pages and {len(images_info)} images.")
            documents.extend(pdf_documents)
            
        except Exception as e:
            print(f"Error loading {pdf_file}: {str(e)}")
    
    print(f"Total documents loaded: {len(documents)}")
    print(f"Total images extracted: {sum(len(images) for images in all_images_info.values())}")
    
    return documents, all_images_info

def process_documents_with_images(documents, all_images_info):
    """
    Process the loaded documents with enhanced image integration.
    
    Args:
        documents (list): List of loaded documents
        all_images_info (dict): Dictionary mapping PDF paths to image information
        
    Returns:
        list: Processed documents with enhanced metadata including images
    """
    if not documents:
        return []
    
    print("Processing documents with enhanced image integration...")
    
    # Use our enhanced sentence-aware text splitter
    text_splitter = EnhancedSentenceAwareTextSplitter(
        chunk_size=1200,  # Slightly larger to accommodate image content
        chunk_overlap=200
    )
    
    split_docs = text_splitter.split_documents_with_images(documents, all_images_info)
    
    # Count documents with images
    docs_with_images = sum(1 for doc in split_docs if doc.metadata.get('has_images', False))
    
    print(f"Split into {len(split_docs)} chunks with enhanced metadata.")
    print(f"{docs_with_images} chunks contain image content.")
    
    return split_docs

def embed_and_save_enhanced_documents(documents, model_name="all-MiniLM-L6-v2"):
    """
    Embed documents (including image content) using HuggingFace sentence-transformers and save with FAISS.
    
    Args:
        documents (list): List of processed documents with image content
        model_name (str): Name of the HuggingFace model to use for embeddings
        
    Returns:
        FAISS: FAISS vector store containing the embedded documents
    """
    if not documents:
        print("No documents to embed.")
        return None
    
    print(f"\nEmbedding documents (including image content) using HuggingFace model: {model_name}")
    
    # Initialize the HuggingFace embeddings
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    
    # Create and save FAISS index
    print("Creating enhanced FAISS index with text and image content...")
    db = FAISS.from_documents(documents, embeddings)
    
    # Save the FAISS index
    output_dir = "./faiss_index"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    db.save_local(output_dir)
    print(f"Enhanced FAISS index saved to {output_dir}")
    
    return db

def main():
    """Main function to run the enhanced PDF loader with image extraction."""
    print("=" * 80)
    print("ENHANCED PDF LOADER WITH IMAGE EXTRACTION")
    print("=" * 80)
    print("Features:")
    print("✓ Text extraction from PDFs")
    print("✓ Image extraction from PDFs")
    print("✓ OCR text extraction from images")
    print("✓ AI-generated image descriptions")
    print("✓ Unified FAISS index for comprehensive search")
    print("=" * 80)
    
    # Load PDFs with enhanced processing
    documents, all_images_info = load_pdfs_with_enhanced_processing()
    
    # Process documents with image integration
    processed_docs = process_documents_with_images(documents, all_images_info)
    
    # Display results
    if processed_docs:
        print("\nSuccessfully loaded and processed PDFs with images.")
        print(f"Total documents processed: {len(processed_docs)}")
        
        # Count and display image statistics
        total_images = sum(len(images) for images in all_images_info.values())
        docs_with_images = sum(1 for doc in processed_docs if doc.metadata.get('has_images', False))
        
        print(f"Total images extracted: {total_images}")
        print(f"Document chunks with images: {docs_with_images}")
        
        # Display sample of the first document with metadata
        if processed_docs:
            print("\nSample of first document content:")
            print("--------------------------------")
            sample_content = processed_docs[0].page_content
            print(sample_content[:500] + "..." if len(sample_content) > 500 else sample_content)
            
            # Display metadata
            print("\nMetadata for this document:")
            print("-------------------------")
            for key, value in processed_docs[0].metadata.items():
                if key in ['image_paths', 'image_descriptions', 'ocr_text']:
                    print(f"{key}: {len(value) if isinstance(value, list) else value} items")
                else:
                    print(f"{key}: {value}")
        
        # Embed documents and save with FAISS
        db = embed_and_save_enhanced_documents(processed_docs)
        
        if db:
            print("\nDocuments with image content have been successfully embedded and saved with FAISS.")
            print("Your AI assistant can now search through both text and image content!")
            
            # Example of similarity search
            print("\nExample similarity search:")
            if len(processed_docs) > 0:
                query = "building connections steel"
                print(f"Query: '{query}'")
                
                results = db.similarity_search(query, k=2)
                print(f"Found {len(results)} similar documents.")
                
                if results:
                    print("\nTop result:")
                    result_content = results[0].page_content
                    print(f"Content: {result_content[:200]}...")
                    
                    # Display metadata for the search result
                    print("\nMetadata for search result:")
                    print("---------------------------")
                    for key, value in results[0].metadata.items():
                        if key in ['image_paths', 'image_descriptions', 'ocr_text']:
                            if isinstance(value, list) and value:
                                print(f"{key}: {len(value)} items")
                                if key == 'image_descriptions' and value:
                                    print(f"  First description: {value[0][:100]}...")
                        else:
                            print(f"{key}: {value}")
    else:
        print("\nNo documents were processed. Please add PDF files to the ./my_pdfs directory.")
    
    print("\n" + "=" * 80)
    print("ENHANCED PDF PROCESSING COMPLETE!")
    print("Your FAISS index now contains both text and image content.")
    print("Run your web QA assistant to search through everything!")
    print("=" * 80)

if __name__ == "__main__":
    main()