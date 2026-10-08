export default function ConceptBand() {
  return (
    <section className="concept" aria-label="How to read this map">
      <div className="concept-claim">
        <span className="dark-box" aria-hidden="true" />
        <span className="not-equal" aria-hidden="true">≠</span>
        <span className="sun-box" aria-hidden="true" />
        <p>
          <strong>Dark does not mean no solar.</strong> Satellites see grid light, not small solar kits.
          This map combines night lights with household surveys, population, wealth, infrastructure and
          solar resource to estimate market reality.
        </p>
      </div>
    </section>
  );
}
