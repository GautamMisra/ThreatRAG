import { useState } from "react";
import "./index.css";

import {
  analyzeSystem,
  type AnalysisResponse,
} from "./services/api";

import ThreatModelView from "./components/ThreatModelView";

type Component = {
  id: number;
  name: string;
  technology: string;
};

type DataFlow = {
  id: number;
  source: string;
  destination: string;
  description: string;
};

function App() {
  const [components, setComponents] = useState<Component[]>([]);
  const [dataFlows, setDataFlows] = useState<DataFlow[]>([]);
  const [trustBoundaries, setTrustBoundaries] = useState<string[]>([]);

  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [componentName, setComponentName] = useState("");
  const [componentTechnology, setComponentTechnology] = useState("");

  const [flowSource, setFlowSource] = useState("");
  const [flowDestination, setFlowDestination] = useState("");
  const [flowDescription, setFlowDescription] = useState("");

  const [boundary, setBoundary] = useState("");

  function addComponent() {
    if (!componentName.trim() || !componentTechnology.trim()) {
      return;
    }

    setComponents((current) => [
      ...current,
      {
        id: Date.now(),
        name: componentName.trim(),
        technology: componentTechnology.trim(),
      },
    ]);

    setComponentName("");
    setComponentTechnology("");
  }

  function removeComponent(id: number) {
    setComponents((current) =>
      current.filter((component) => component.id !== id)
    );
  }

  function addDataFlow() {
    if (
      !flowSource.trim() ||
      !flowDestination.trim() ||
      !flowDescription.trim()
    ) {
      return;
    }

    setDataFlows((current) => [
      ...current,
      {
        id: Date.now(),
        source: flowSource.trim(),
        destination: flowDestination.trim(),
        description: flowDescription.trim(),
      },
    ]);

    setFlowSource("");
    setFlowDestination("");
    setFlowDescription("");
  }

  function removeDataFlow(id: number) {
    setDataFlows((current) =>
      current.filter((flow) => flow.id !== id)
    );
  }

  function addTrustBoundary() {
    if (!boundary.trim()) {
      return;
    }

    setTrustBoundaries((current) => [...current, boundary.trim()]);
    setBoundary("");
  }

  function removeTrustBoundary(index: number) {
    setTrustBoundaries((current) =>
      current.filter((_, i) => i !== index)
    );
  }

  async function handleAnalyze() {
    if (components.length === 0) {
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysis(null);

    try {
      const result = await analyzeSystem({
        components: components.map(({ name, technology }) => ({
          name,
          technology,
        })),
        data_flows: dataFlows.map(
          ({ source, destination, description }) => ({
            source,
            destination,
            description,
          })
        ),
        trust_boundaries: trustBoundaries,
      });

      setAnalysis(result);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "An unexpected error occurred during analysis.";

      setError(message);
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">SECURITY ANALYSIS</p>
          <h1>ThreatRAG</h1>
        </div>

        <div className="status-indicator">
          <span className="status-dot" />
          Local analysis
        </div>
      </header>

      <main className="main-content">
        <section className="intro">
          <p className="section-label">THREAT MODEL</p>

          <h2>Describe the system architecture</h2>

          <p>
            Define the components, data flows, and trust boundaries that make
            up the system. ThreatRAG will use the architecture as input to its
            retrieval and threat synthesis pipeline.
          </p>
        </section>

        <section className="workspace">
          {/* Components */}
          <div className="panel">
            <div className="panel-header">
              <div>
                <p className="section-label">01 / COMPONENTS</p>
                <h3>System components</h3>
              </div>

              <span className="count">{components.length}</span>
            </div>

            <div className="form-grid">
              <label>
                <span>Component name</span>
                <input
                  type="text"
                  placeholder="e.g. Auth Service"
                  value={componentName}
                  onChange={(e) => setComponentName(e.target.value)}
                />
              </label>

              <label>
                <span>Technology</span>
                <input
                  type="text"
                  placeholder="e.g. JWT"
                  value={componentTechnology}
                  onChange={(e) =>
                    setComponentTechnology(e.target.value)
                  }
                />
              </label>
            </div>

            <button
              className="secondary-button"
              type="button"
              onClick={addComponent}
              disabled={
                !componentName.trim() ||
                !componentTechnology.trim()
              }
            >
              + Add component
            </button>

            <div className="item-list">
              {components.length === 0 ? (
                <div className="empty-state">
                  <strong>No components added</strong>
                  <span>
                    Add the services, clients, databases, or infrastructure
                    involved in the system.
                  </span>
                </div>
              ) : (
                components.map((component) => (
                  <article className="list-item" key={component.id}>
                    <div>
                      <strong>{component.name}</strong>
                      <span>{component.technology}</span>
                    </div>

                    <button
                      className="remove-button"
                      type="button"
                      onClick={() => removeComponent(component.id)}
                      aria-label={`Remove ${component.name}`}
                    >
                      Remove
                    </button>
                  </article>
                ))
              )}
            </div>
          </div>

          {/* Data flows */}
          <div className="panel">
            <div className="panel-header">
              <div>
                <p className="section-label">02 / DATA FLOWS</p>
                <h3>System communication</h3>
              </div>

              <span className="count">{dataFlows.length}</span>
            </div>

            <div className="form-grid">
              <label>
                <span>Source</span>
                <input
                  type="text"
                  placeholder="e.g. Browser"
                  value={flowSource}
                  onChange={(e) => setFlowSource(e.target.value)}
                />
              </label>

              <label>
                <span>Destination</span>
                <input
                  type="text"
                  placeholder="e.g. Auth Service"
                  value={flowDestination}
                  onChange={(e) =>
                    setFlowDestination(e.target.value)
                  }
                />
              </label>
            </div>

            <label>
              <span>Data / communication</span>
              <textarea
                placeholder="e.g. Credentials and JWT access token"
                value={flowDescription}
                onChange={(e) =>
                  setFlowDescription(e.target.value)
                }
                rows={3}
              />
            </label>

            <button
              className="secondary-button"
              type="button"
              onClick={addDataFlow}
              disabled={
                !flowSource.trim() ||
                !flowDestination.trim() ||
                !flowDescription.trim()
              }
            >
              + Add data flow
            </button>

            <div className="item-list">
              {dataFlows.length === 0 ? (
                <div className="empty-state">
                  <strong>No data flows added</strong>
                  <span>
                    Define how information moves between components.
                  </span>
                </div>
              ) : (
                dataFlows.map((flow) => (
                  <article className="list-item" key={flow.id}>
                    <div>
                      <strong>
                        {flow.source} → {flow.destination}
                      </strong>
                      <span>{flow.description}</span>
                    </div>

                    <button
                      className="remove-button"
                      type="button"
                      onClick={() => removeDataFlow(flow.id)}
                      aria-label="Remove data flow"
                    >
                      Remove
                    </button>
                  </article>
                ))
              )}
            </div>
          </div>

          {/* Trust boundaries */}
          <div className="panel full-width">
            <div className="panel-header">
              <div>
                <p className="section-label">03 / TRUST BOUNDARIES</p>
                <h3>Trust boundary crossings</h3>
              </div>

              <span className="count">{trustBoundaries.length}</span>
            </div>

            <div className="inline-form">
              <label>
                <span>Boundary</span>
                <input
                  type="text"
                  placeholder="e.g. Internet → Application"
                  value={boundary}
                  onChange={(e) => setBoundary(e.target.value)}
                />
              </label>

              <button
                className="secondary-button"
                type="button"
                onClick={addTrustBoundary}
                disabled={!boundary.trim()}
              >
                + Add boundary
              </button>
            </div>

            {trustBoundaries.length > 0 && (
              <div className="boundary-list">
                {trustBoundaries.map((item, index) => (
                  <div className="boundary-item" key={`${item}-${index}`}>
                    <span>{item}</span>

                    <button
                      className="remove-button"
                      type="button"
                      onClick={() => removeTrustBoundary(index)}
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        {isAnalyzing && (
          <section className="analysis-progress" aria-live="polite">
            <div className="progress-indicator" />

            <div>
              <p className="section-label">
                ANALYSIS IN PROGRESS
              </p>

              <strong>
                Retrieving and synthesizing security evidence
              </strong>

              <span>
                The local RAG pipeline is analyzing the submitted
                architecture.
              </span>
            </div>
          </section>
        )}

        {/* Analysis */}
        <section className="analysis-section">
          <div>
            <p className="section-label">READY FOR ANALYSIS</p>
            <p className="analysis-summary">
              {components.length} component
              {components.length !== 1 ? "s" : ""} ·{" "}
              {dataFlows.length} data flow
              {dataFlows.length !== 1 ? "s" : ""} ·{" "}
              {trustBoundaries.length} trust boundary
              {trustBoundaries.length !== 1 ? "ies" : "y"}
            </p>
          </div>

          <button
            className="primary-button"
            type="button"
            onClick={handleAnalyze}
            disabled={components.length === 0 || isAnalyzing}
          >
            {isAnalyzing ? "Analyzing system..." : "Generate threat model"}
          </button>
        </section>
        {error && (
          <section className="error-message" role="alert">
            <div>
              <p className="section-label">ANALYSIS FAILED</p>
              <strong>{error}</strong>
            </div>

            <button
              className="remove-button"
              type="button"
              onClick={() => setError(null)}
            >
              Dismiss
            </button>
          </section>
        )}
        {analysis && (
          <ThreatModelView analysis={analysis} />
        )}
      </main>
    </div>
  );
}

export default App;
