import AsyncView from "../components/AsyncView";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";

export default function DataPage({ meta }) {
  const sources = useApi(() => api.dataSources(), []);
  return (
    <div className="stack">
      <h2 className="page-title">Data sources</h2>
      <p className="muted">
        How the result is built: surveys provide the labels, every other dataset is a predictive feature,
        and GOGLA is only a national sanity check.
        {meta.is_demo && " In this run every dataset is replaced by the synthetic substitute listed on each card."}
      </p>
      <AsyncView state={sources} isEmpty={(d) => !d.length} empty="No data sources are documented yet.">
        {(list) => (
          <div className="grid-2">
            {list.map((d) => (
              <article key={d.id} className="panel source">
                <h3>{d.name}</h3>
                <p>{d.description}</p>
                <dl>
                  <div className="kv"><dt>Role in model</dt><dd>{d.role}</dd></div>
                  <div className="kv"><dt>Year</dt><dd>{d.year}</dd></div>
                  <div className="kv"><dt>Resolution</dt><dd>{d.resolution}</dd></div>
                  <div className="kv"><dt>Limitations</dt><dd>{d.limitations}</dd></div>
                  {meta.is_demo && <div className="kv"><dt>Demo substitute</dt><dd>{d.demo_substitute}</dd></div>}
                </dl>
              </article>
            ))}
          </div>
        )}
      </AsyncView>
    </div>
  );
}
