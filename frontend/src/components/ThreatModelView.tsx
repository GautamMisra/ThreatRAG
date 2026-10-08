import type {
    AnalysisResponse,
    Threat,
} from "../services/api";

type Props = {
    analysis: AnalysisResponse;
};

function ThreatRow({ threat }: { threat: Threat }) {
    return (
        <tr>
            <td>
                <span className="stride-category">
                    {threat.stride_category}
                </span>
            </td>

            <td>
                <strong className="threat-name">
                    {threat.threat}
                </strong>
            </td>

            <td>
                <span className="risk-value">
                    {threat.likelihood}
                </span>
            </td>

            <td>
                <span className="risk-value">
                    {threat.impact}
                </span>
            </td>

            <td className="mitigation-cell">
                {threat.mitigation}
            </td>

            <td>
                <div className="source-cell">
                    <span>{threat.source}</span>

                    <code>{threat.source_id}</code>

                    <small>{threat.source_title}</small>
                </div>
            </td>
        </tr>
    );
}

export default function ThreatModelView({
    analysis,
}: Props) {
    const totalThreats = analysis.components.reduce(
        (total, component) =>
            total + component.threat_model.threats.length,
        0
    );

    const totalGrounded = analysis.components.reduce(
        (total, component) =>
            total +
            component.threat_model.grounding.grounded_threats,
        0
    );

    const totalRejected = analysis.components.reduce(
        (total, component) =>
            total +
            component.threat_model.grounding.rejected_threats,
        0
    );

    return (
        <section className="results-section">
            <div className="results-header">
                <div>
                    <p className="section-label">
                        04 / THREAT MODEL
                    </p>

                    <h2>Analysis results</h2>

                    <p className="results-description">
                        Threats synthesized from retrieved STRIDE,
                        MITRE ATT&CK, and OWASP context.
                    </p>
                </div>

                <div className="results-meta">
                    <span>
                        {analysis.components.length} components
                    </span>

                    <span>·</span>

                    <span>{totalThreats} threats</span>

                    <span>·</span>

                    <span>{totalGrounded} grounded</span>
                </div>
            </div>

            {/* Grounding overview */}
            <div className="grounding-bar">
                <div>
                    <span className="grounding-label">
                        EVIDENCE GROUNDING
                    </span>

                    <strong>
                        {totalGrounded}/{totalThreats} threats grounded
                    </strong>
                </div>

                <div className="grounding-status">
                    <span className="grounded-dot" />

                    All generated threats are linked to retrieved
                    evidence
                </div>

                {totalRejected > 0 && (
                    <div className="rejected-status">
                        {totalRejected} rejected
                    </div>
                )}
            </div>

            <div className="component-results">
                {analysis.components.map((component) => {
                    const { threat_model } = component;

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

                                <div className="component-grounding">
                                    <span>
                                        {threat_model.threats.length}{" "}
                                        {threat_model.threats.length === 1
                                            ? "threat"
                                            : "threats"}
                                    </span>

                                    <span className="grounded-label">
                                        {threat_model.grounding.grounded_threats}{" "}
                                        grounded
                                    </span>
                                </div>
                            </header>

                            <div className="component-summary">
                                <p>{threat_model.summary}</p>
                            </div>

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
                                        {threat_model.threats.map(
                                            (threat, index) => (
                                                <ThreatRow
                                                    key={`${threat.source_id}-${index}`}
                                                    threat={threat}
                                                />
                                            )
                                        )}
                                    </tbody>
                                </table>
                            </div>

                            {/* Evidence */}
                            <div className="evidence-section">
                                <div className="evidence-header">
                                    <div>
                                        <p className="section-label">
                                            RETRIEVED EVIDENCE
                                        </p>

                                        <h4>Grounding trail</h4>
                                    </div>
                                </div>

                                <div className="evidence-list">
                                    {threat_model.threats.map(
                                        (threat, index) => (
                                            <article
                                                className="evidence-item"
                                                key={`${threat.source_id}-evidence-${index}`}
                                            >
                                                <div className="evidence-meta">
                                                    <span>
                                                        {threat.source}
                                                    </span>

                                                    <code>
                                                        {threat.source_id}
                                                    </code>

                                                    <span>
                                                        {threat.source_title}
                                                    </span>

                                                    {threat.grounded && (
                                                        <span className="grounded-badge">
                                                            GROUNDED
                                                        </span>
                                                    )}
                                                </div>

                                                <p>{threat.evidence}</p>
                                            </article>
                                        )
                                    )}
                                </div>
                            </div>

                            {/* Recommendations */}
                            {threat_model.recommendations.length >
                                0 && (
                                    <div className="recommendations-section">
                                        <p className="section-label">
                                            RECOMMENDATIONS
                                        </p>

                                        <ul>
                                            {threat_model.recommendations.map(
                                                (recommendation, index) => (
                                                    <li key={index}>
                                                        {recommendation}
                                                    </li>
                                                )
                                            )}
                                        </ul>
                                    </div>
                                )}
                        </article>
                    );
                })}
            </div>
        </section>
    );
}