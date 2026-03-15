// Service line default templates
// When a service_line is selected, these defaults are merged under the user-provided params

const SERVICE_LINE_DEFAULTS = {
  capital_planning: {
    workshop_title: "Capital Planning & Portfolio Intelligence \u2014 Discovery Workshop",
    service_line_label: "Capital Planning & Portfolio Intelligence",
    context:
      "You manage a complex capital programme across multiple concurrent projects. The challenge of maintaining portfolio-level visibility, enabling rapid scenario modelling, and supporting executive decision governance is a known constraint on planning effectiveness.",
    pain_points: [
      "Limited portfolio-level visibility across concurrent capital projects",
      "Manual reporting processes that slow decision cycles",
      "Difficulty modelling scenario trade-offs at pace for executive governance",
      "Data fragmentation across systems and project teams",
    ],
    objectives: [
      "Map current state of capital planning data flows and reporting",
      "Identify highest-value decision points where AI can accelerate insight",
      "Demonstrate the Blue Harbour Decision Engine on a live scenario",
      "Define a pilot scope and success criteria for a 90-day engagement",
    ],
    deliverables: [
      "Current state map of capital planning data flows and decision points",
      "Prioritised list of AI acceleration opportunities",
      "Draft pilot scope document with success criteria",
      "Proposed 90-day roadmap for Decision Engine deployment",
    ],
  },

  ai_agents: {
    workshop_title: "Intelligent Agent Services \u2014 Discovery Workshop",
    service_line_label: "Intelligent Agent Services",
    context:
      "AI agents connected to your data environment can automate decisions, surface insights, and accelerate workflows across a broad range of use cases. This workshop identifies where agents create the most immediate value in your organisation.",
    pain_points: [
      "High-volume repetitive analytical tasks consuming skilled staff time",
      "Slow turnaround on data queries and insight requests",
      "Manual handoffs between systems creating bottlenecks",
      "Opportunity to automate decisions at the point of data availability",
    ],
    objectives: [
      "Identify the top 3-5 agent automation opportunities in your environment",
      "Map the data sources and access requirements for each",
      "Demonstrate a working agent against a sample dataset",
      "Define a pilot scope for the highest-value automation",
    ],
    deliverables: [
      "Ranked list of agent automation opportunities with effort/value mapping",
      "Data source and access requirements for top candidates",
      "Working demonstration agent against sample data",
      "Pilot scope and 90-day roadmap for first agent deployment",
    ],
  },

  reporting: {
    workshop_title: "Intelligent Reporting Platform \u2014 Discovery Workshop",
    service_line_label: "Intelligent Reporting Platform",
    context:
      "Your organisation produces significant reporting output, often manually and at high effort. The Intelligent Reporting Platform combines AI-assisted data modelling with Power BI and a web-accessible interface to deliver reporting at dramatically higher speed and quality.",
    pain_points: [
      "Report production consuming disproportionate analyst time",
      "Inconsistent data definitions across reporting outputs",
      "Slow turnaround on ad-hoc reporting requests",
      "Limited ability to explore data dynamically at executive level",
    ],
    objectives: [
      "Audit current reporting outputs, data sources, and production effort",
      "Identify the highest-value reports for AI-assisted automation",
      "Demonstrate the Intelligent Reporting Platform on a live dataset",
      "Define a pilot scope for the first automated reporting workflow",
    ],
    deliverables: [
      "Audit of current reporting outputs with effort and frequency mapping",
      "Prioritised list of reports for AI-assisted automation",
      "Live demonstration of the Intelligent Reporting Platform",
      "Pilot scope and timeline for first automated reporting workflow",
    ],
  },

  data_enablement: {
    workshop_title: "Data Enablement \u2014 Discovery Workshop",
    service_line_label: "Data Enablement",
    context:
      "Unlocking the value in your data environment requires clarity on what data exists, how it flows, and where the highest-value opportunities for integration and automation sit. This workshop maps your data landscape and identifies the fastest path to measurable value.",
    pain_points: [
      "Data scattered across multiple systems with limited integration",
      "Unclear data ownership and governance across teams",
      "Manual data preparation consuming analyst capacity",
      "Difficulty connecting data assets to business decision points",
    ],
    objectives: [
      "Map current data sources, flows, and ownership",
      "Identify the highest-value data integration opportunities",
      "Demonstrate AI-assisted data modelling on a sample dataset",
      "Define a pilot scope for the first data enablement initiative",
    ],
    deliverables: [
      "Data landscape map with sources, flows, and ownership",
      "Prioritised list of data integration opportunities",
      "Demonstration of AI-assisted data modelling",
      "Pilot scope and 90-day roadmap for data enablement",
    ],
  },

  generic: {
    workshop_title: "Discovery Workshop",
    service_line_label: "Advisory Services",
    context: "",
    pain_points: [],
    objectives: [],
    deliverables: [],
  },
};

const DEFAULT_AGENDA = [
  { time: "9:00am", item: "Welcome & context setting", duration: "15 min" },
  { time: "9:15am", item: "Current state mapping \u2014 data, reporting, decision flows", duration: "45 min" },
  { time: "10:00am", item: "Live demonstration \u2014 Decision Engine on relevant scenario", duration: "30 min" },
  { time: "10:30am", item: "Break", duration: "15 min" },
  { time: "10:45am", item: "Opportunity identification & prioritisation", duration: "45 min" },
  { time: "11:30am", item: "Pilot scope definition & next steps", duration: "30 min" },
  { time: "12:00pm", item: "Close", duration: "" },
];

const COMMON_DEFAULTS = {
  workshop_duration: "Half day (4 hours)",
  workshop_format: "In-person, client offices",
  workshop_fee: "No charge \u2014 complimentary discovery session",
  bh_lead: "Dr Dave Braendler",
  bh_lead_title: "Founder & Principal, Blue Harbour",
  bh_support: "Frequency NZ (delivery partner)",
  bh_email: "dave.braendler@blueharbour.ai",
  bh_phone: "022 189 7455",
  bh_web: "blueharbour.ai",
};

module.exports = { SERVICE_LINE_DEFAULTS, DEFAULT_AGENDA, COMMON_DEFAULTS };
