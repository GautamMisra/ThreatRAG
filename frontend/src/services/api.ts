const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

export type ComponentInput = {
  name: string;
  technology: string;
};

export type DataFlowInput = {
  source: string;
  destination: string;
  description: string;
};

export type SystemDescription = {
  components: ComponentInput[];
  data_flows: DataFlowInput[];
  trust_boundaries: string[];
};

export type Threat = {
  stride_category: string;
  threat: string;
  likelihood: string;
  impact: string;
  mitigation: string;
  source: string;
  source_id: string;
  source_title: string;
  evidence: string;
  grounded: boolean;
};

export type GroundingStats = {
  total_threats_generated: number;
  grounded_threats: number;
  rejected_threats: number;
};

export type ThreatModel = {
  summary: string;
  threats: Threat[];
  recommendations: string[];
  grounding: GroundingStats;
};

export type ComponentAnalysis = {
  component: string;
  technology: string;
  threat_model: ThreatModel;
};

export type AnalysisResponse = {
  status: string;
  components: ComponentAnalysis[];
  data_flows: DataFlowInput[];
  trust_boundaries: string[];
};

export async function analyzeSystem(
  system: SystemDescription
): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(system),
  });

  if (!response.ok) {
    let message = `Analysis failed (${response.status})`;

    try {
      const error = await response.json();

      if (typeof error.detail === "string") {
        message = error.detail;
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(message);
  }

  return response.json();
}