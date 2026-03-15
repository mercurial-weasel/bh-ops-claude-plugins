const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, ShadingType, LevelFormat,
  Footer, Header
} = require('docx');

// ============================================================
// DOCUMENT BUILDER — pure function: params → docx Buffer
// ============================================================

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

const divider = (color = "1B3A6B") => new Paragraph({
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color, space: 4 } },
  spacing: { before: 160, after: 160 }
});

const bodyPara = (text, italic = false, color = "333333") => new Paragraph({
  spacing: { before: 80, after: 80 },
  children: [new TextRun({ text, italic, font: "Arial", size: 20, color })]
});

const bullet = (text, color = "333333") => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  spacing: { before: 60, after: 60 },
  children: [new TextRun({ text, font: "Arial", size: 20, color })]
});

const sectionTitle = (text, color = "1B3A6B") => new Paragraph({
  spacing: { before: 240, after: 100 },
  children: [new TextRun({ text, bold: true, font: "Arial", size: 26, color })]
});

const cell = (text, bold = false, shaded = false, width = 4513, color = "333333") => new TableCell({
  borders,
  width: { size: width, type: WidthType.DXA },
  shading: { fill: shaded ? "EEF3FA" : "FFFFFF", type: ShadingType.CLEAR },
  margins: { top: 80, bottom: 80, left: 120, right: 120 },
  children: [new Paragraph({ children: [new TextRun({ text, bold, font: "Arial", size: 20, color })] })]
});

const headerCell = (text, width = 4513, fill = "1B3A6B") => new TableCell({
  borders,
  width: { size: width, type: WidthType.DXA },
  shading: { fill, type: ShadingType.CLEAR },
  margins: { top: 80, bottom: 80, left: 120, right: 120 },
  children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })]
});

const numberedItem = (index, text) => new Paragraph({
  spacing: { before: 80, after: 80 },
  children: [
    new TextRun({ text: `${index}.  `, bold: true, font: "Arial", size: 20, color: "1B3A6B" }),
    new TextRun({ text, font: "Arial", size: 20, color: "333333" })
  ]
});

/**
 * Build a proposal document from merged params.
 * @param {object} params - Fully merged parameters (defaults already applied)
 * @returns {Promise<Buffer>} - The .docx file as a Buffer
 */
async function buildProposal(params) {
  const p = params;

  const doc = new Document({
    numbering: {
      config: [{
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      }]
    },
    styles: {
      default: { document: { run: { font: "Arial", size: 20, color: "333333" } } }
    },
    sections: [{
      properties: {
        page: {
          size: { width: 11906, height: 16838 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      headers: {
        default: new Header({
          children: [
            new Table({
              width: { size: 9026, type: WidthType.DXA },
              columnWidths: [6000, 3026],
              rows: [new TableRow({ children: [
                new TableCell({ borders: noBorders, children: [
                  new Paragraph({ children: [new TextRun({ text: "Blue Harbour", bold: true, font: "Arial", size: 22, color: "1B3A6B" })] }),
                  new Paragraph({ children: [new TextRun({ text: p.bh_web, font: "Arial", size: 18, color: "888888" })] }),
                ]}),
                new TableCell({ borders: noBorders, children: [
                  new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: `Ref: ${p.proposal_ref}`, font: "Arial", size: 18, color: "888888" })] }),
                  new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: p.proposal_date, font: "Arial", size: 18, color: "888888" })] }),
                ]}),
              ]})]
            }),
            new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: "1B3A6B" } }, spacing: { before: 80, after: 80 }, children: [] }),
          ]
        })
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({ border: { top: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" } }, spacing: { before: 80, after: 0 }, children: [] }),
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [new TextRun({ text: `Blue Harbour  |  ${p.bh_email}  |  ${p.bh_phone}  |  Confidential`, font: "Arial", size: 16, color: "888888" })]
            })
          ]
        })
      },
      children: [
        // Cover block
        new Paragraph({ spacing: { before: 400, after: 120 }, children: [new TextRun({ text: "Workshop Proposal", bold: true, font: "Arial", size: 48, color: "1B3A6B" })] }),
        new Paragraph({ spacing: { before: 0, after: 80 }, children: [new TextRun({ text: p.workshop_title, bold: true, font: "Arial", size: 28, color: "2C5F9E" })] }),
        new Paragraph({ spacing: { before: 0, after: 320 }, children: [new TextRun({ text: `Prepared for ${p.client_contact}, ${p.client_title} \u2014 ${p.client_name}`, font: "Arial", size: 20, color: "555555" })] }),

        divider(),

        // Proposal summary table
        sectionTitle("Proposal Summary"),
        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [2800, 6226],
          rows: [
            new TableRow({ children: [cell("Client", true, true, 2800), cell(p.client_name, false, true, 6226)] }),
            new TableRow({ children: [cell("Contact", true, false, 2800), cell(`${p.client_contact}, ${p.client_title}`, false, false, 6226)] }),
            new TableRow({ children: [cell("Service Line", true, true, 2800), cell(p.service_line_label || p.service_line, false, true, 6226)] }),
            new TableRow({ children: [cell("Workshop Format", true, false, 2800), cell(p.workshop_format, false, false, 6226)] }),
            new TableRow({ children: [cell("Duration", true, true, 2800), cell(p.workshop_duration, false, true, 6226)] }),
            new TableRow({ children: [cell("Proposed Date", true, false, 2800), cell(p.proposed_date || "To be confirmed", false, false, 6226)] }),
            new TableRow({ children: [cell("Investment", true, true, 2800), cell(p.workshop_fee, false, true, 6226)] }),
            new TableRow({ children: [cell("Proposal Valid Until", true, false, 2800), cell(p.proposal_expiry, false, false, 6226)] }),
          ]
        }),

        divider(),

        // Context
        sectionTitle("Context & Opportunity"),
        bodyPara(p.context),
        new Paragraph({ spacing: { before: 120, after: 80 }, children: [new TextRun({ text: "Key challenges we understand you are navigating:", font: "Arial", size: 20, color: "333333" })] }),
        ...p.pain_points.map(pt => bullet(pt)),

        divider(),

        // Objectives
        sectionTitle("Workshop Objectives"),
        bodyPara("This workshop is designed to achieve the following outcomes:"),
        ...p.objectives.map((o, i) => numberedItem(i + 1, o)),

        divider(),

        // Agenda
        sectionTitle("Proposed Agenda"),
        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [1400, 5626, 2000],
          rows: [
            new TableRow({ children: [headerCell("Time", 1400), headerCell("Item", 5626), headerCell("Duration", 2000)] }),
            ...p.agenda.map((a, i) => new TableRow({ children: [
              cell(a.time, false, i % 2 === 0, 1400),
              cell(a.item, false, i % 2 === 0, 5626),
              cell(a.duration || "", false, i % 2 === 0, 2000),
            ]}))
          ]
        }),

        divider(),

        // Deliverables
        sectionTitle("What You Will Leave With"),
        bodyPara("At the close of the workshop, you will have:"),
        ...p.deliverables.map(d => bullet(d)),

        divider(),

        // Investment
        sectionTitle("Investment"),
        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [3600, 5426],
          rows: [
            new TableRow({ children: [headerCell("Item", 3600), headerCell("Investment", 5426)] }),
            new TableRow({ children: [cell("Discovery Workshop", true, true, 3600), cell(p.workshop_fee, false, true, 5426)] }),
            ...(p.follow_on_indicative ? [new TableRow({ children: [cell("Indicative follow-on pilot", true, false, 3600), cell(p.follow_on_indicative, false, false, 5426)] })] : []),
          ]
        }),
        bodyPara("The discovery workshop is offered at no charge as a genuine investment in understanding your environment. There is no obligation to proceed beyond it.", true),

        divider(),

        // Team
        sectionTitle("Your Blue Harbour Team"),
        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [2800, 6226],
          rows: [
            new TableRow({ children: [headerCell("Role", 2800), headerCell("Person / Organisation", 6226)] }),
            new TableRow({ children: [cell("Workshop Lead", true, true, 2800), cell(`${p.bh_lead} \u2014 ${p.bh_lead_title}`, false, true, 6226)] }),
            new TableRow({ children: [cell("Delivery Support", true, false, 2800), cell(p.bh_support, false, false, 6226)] }),
          ]
        }),

        divider(),

        // Next steps
        sectionTitle("Next Steps"),
        numberedItem(1, "Confirm your interest and preferred date by replying to this proposal"),
        numberedItem(2, "Blue Harbour will confirm logistics and send a pre-workshop questionnaire"),
        numberedItem(3, "Workshop delivered, outcomes documented and pilot scope agreed"),
        new Paragraph({ spacing: { before: 160, after: 80 }, children: [
          new TextRun({ text: "To proceed or ask any questions, contact ", font: "Arial", size: 20, color: "333333" }),
          new TextRun({ text: p.bh_lead, bold: true, font: "Arial", size: 20, color: "1B3A6B" }),
          new TextRun({ text: ` at ${p.bh_email} or ${p.bh_phone}.`, font: "Arial", size: 20, color: "333333" }),
        ]}),

        divider(),

        bodyPara("This proposal is confidential and prepared solely for the named recipient. It does not constitute a binding agreement.", true, "888888"),
        bodyPara(`Blue Harbour  |  ${p.bh_web}  |  ${p.bh_email}`, true, "888888"),
      ]
    }]
  });

  return Packer.toBuffer(doc);
}

module.exports = { buildProposal };
