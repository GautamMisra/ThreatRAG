import type { AnalysisResponse } from "../services/api";

type Props = {
    analysis: AnalysisResponse;
};

type Threat = {
    stride_category?: string;
    threat?: string;
    mitigation?: string;
    likelihood?: string;
    impact?: string;
    source?: string;
    citation?: string;
    technique?: string;
    technique_id?: string;
    [key: string]: unknown;
};

function getThreats(threatModel: Record<string, unknown>): Threat[] {
    if (Array.isArray(threatModel.threats)) {
        return threatModel.threats as Threat[];
    }

    return [];
}

function getString(
    value: unknown,
    fallback = "Not specified"
): string {
    return typeof value === "string" && value.trim()
        ? value
        : fallback;
}

export default function ThreatModelView({ analysis }: Props) {
    const totalThreats = analysis.components.reduce(
        (total, component) =>
            total +
            getThreats(component.threat_model).length,
        0
    );

    return (
        <section className="results-section">
            <div className="results-header">
                <div>
                    <p className="section-label">04 / THREAT MODEL</p>
                    <h2>Analysis results</h2>
                    <p className="results-description">
                        Threats synthesized from the retrieved STRIDE, MITRE ATT&CK,
                        and OWASP context.
                    </p>
                </div>

                <div className="results-meta">
                    <span>
                        {analysis.components.length} component
                        {analysis.components.length !== 1 ? "s" : ""}
                    </span>

                    <span>·</span>

                    <span>
                        {totalThreats} threat
                        {totalThreats !== 1 ? "s" : ""}
                    </span>
                </div>
            </div>

            <div className="component-results">
                {analysis.components.map((component) => {
                    const threats = getThreats(component.threat_model);

                    const summary = getString(
                        component.threat_model.summary,
                        ""
                    );

                    return (
                        <article
                            className="component-result"
                            key={`${component.component}-${component.technology}`}
                        >
                            <header className="component-result-header">
                                <div>
                                    <p className="component-number">
                                        COMPONENT
                                    </p>

                                    <h3>{component.component}</h3>

                                    <span className="technology">
                                        {component.technology}
                                    </span>
                                </div>

                                <span className="threat-count">
                                    {threats.length}{" "}
                                    {threats.length === 1 ? "threat" : "threats"}
                                </span>
                            </header>

                            {summary && (
                                <div className="component-summary">
                                    <p>{summary}</p>
                                </div>
                            )}

                            {threats.length === 0 ? (
                                <div className="no-threats">
                                    No structured threats were returned for this
                                    component.
                                </div>
                            ) : (
                                <div className="threat-table-wrapper">
                                    <table className="threat-table">
                                        <thead>
                                            <tr>
                                                <th>STRIDE</th>
                                                <th>Threat</th>
                                                <th>Likelihood</th>
                                                <th>Impact</th>
                                                <th>Mitigation</th>
                                                <th>Source</th>
                                            </tr>
                                        </thead>

                                        <tbody>
                                            {threats.map((threat, index) => {
                                                const source =
                                                    getString(threat.source, "");

                                                const citation =
                                                    getString(threat.citation, "");

                                                const technique =
                                                    getString(threat.technique, "");

                                                const techniqueId =
                                                    getString(
                                                        threat.technique_id,
                                                        ""
                                                    );

                                                return (
                                                    <tr key={index}>
                                                        <td>
                                                            <span className="stride-category">
                                                                {getString(
                                                                    threat.stride_category
                                                                )}
                                                            </span>
                                                        </td>

                                                        <td>
                                                            <strong className="threat-name">
                                                                {getString(threat.threat)}
                                                            </strong>

                                                            {(technique ||
                                                                techniqueId) && (
                                                                    <span className="technique">
                                                                        {techniqueId}
                                                                        {techniqueId &&
                                                                            technique &&
                                                                            " · "}
                                                                        {technique}
                                                                    </span>
                                                                )}
                                                        </td>

                                                        <td>
                                                            {getString(
                                                                threat.likelihood
                                                            )}
                                                        </td>

                                                        <td>
                                                            {getString(threat.impact)}
                                                        </td>

                                                        <td className="mitigation-cell">
                                                            {getString(
                                                                threat.mitigation
                                                            )}
                                                        </td>

                                                        <td>
                                                            <div className="source-cell">
                                                                {source && (
                                                                    <span>{source}</span>
                                                                )}

                                                                {citation && (
                                                                    <code>{citation}</code>
                                                                )}

                                                                {!source &&
                                                                    !citation && (
                                                                        <span>
                                                                            Retrieved context
                                                                        </span>
                                                                    )}
                                                            </div>
                                                        </td>
                                                    </tr>
                                                );
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </article>
                    );
                })}
            </div>
        </section>
    );
}