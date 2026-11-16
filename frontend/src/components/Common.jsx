import React, { useEffect } from "react";
import { statusClass, statusLabel } from "../constants/status.js";
import { dateTime } from "../utils/formatters.js";

export function Status({ value }) {
  return (
    <span className={`status status-${statusClass(value)}`}>
      {statusLabel(value)}
    </span>
  );
}

export function Metric({ label, value, description, icon = "✦" }) {
  return (
    <article className="metric-card">
      <div className="metric-top">
        <span>{label}</span>
        <i>{icon}</i>
      </div>
      <strong>{value}</strong>
      {description && <small>{description}</small>}
    </article>
  );
}

export function SectionTitle({
  eyebrow,
  title,
  description,
  action,
}) {
  return (
    <div className="section-title">
      <div>
        {eyebrow && <span className="eyebrow">{eyebrow}</span>}
        <h2>{title}</h2>
        {description && <p>{description}</p>}
      </div>
      {action}
    </div>
  );
}

export function Empty({ title = "Nenhum registro encontrado" }) {
  return (
    <div className="empty-state">
      <strong>{title}</strong>
      <p>Os dados aparecerão aqui quando estiverem disponíveis.</p>
    </div>
  );
}

export function Field({ label, children, hint }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
      {hint && <small>{hint}</small>}
    </label>
  );
}

export function FormActions({
  submitLabel = "Salvar",
  cancelLabel,
  onCancel,
}) {
  return (
    <div className="form-actions">
      {cancelLabel && (
        <button
          type="button"
          className="primary-button"
          onClick={onCancel}
        >
          {cancelLabel}
        </button>
      )}

      <button type="submit" className="primary-button">
        {submitLabel}
      </button>
    </div>
  );
}

export function ShipsList({ ships }) {
  return (
    <section className="panel">
      <SectionTitle
        title="Naves cadastradas"
        description="Consulte a frota disponível no sistema."
      />

      {ships.length ? (
        <div className="ship-grid">
          {ships.map(ship => (
            <article className="ship-card" key={ship.id}>
              <div className="ship-card-icon">✦</div>
              <h3>{ship.name}</h3>
              <p>Capacidade total</p>
              <strong>{ship.total_capacity} assentos</strong>
              <Status value={ship.status} />
            </article>
          ))}
        </div>
      ) : (
        <Empty title="Nenhuma nave cadastrada" />
      )}
    </section>
  );
}

export function MissionsList({ missions, onSelect }) {
  return (
    <section className="panel">
      <SectionTitle
        title="Missões cadastradas"
        description="Consulte e acompanhe as operações de resgate."
      />

      {missions.length ? (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Missão</th>
                <th>Estação</th>
                <th>Passageiros</th>
                <th>Urgência</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {missions.map(mission => (
                <tr key={mission.id}>
                  <td>{mission.name}</td>
                  <td>{mission.station}</td>
                  <td>{mission.people_count}</td>
                  <td>{mission.urgency}</td>
                  <td><Status value={mission.status} /></td>
                  <td>
                    <button
                      type="button"
                      className="primary-button"
                      onClick={() => onSelect(mission.id)}
                    >
                      Acompanhar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <Empty title="Nenhuma missão cadastrada" />
      )}
    </section>
  );
}

export function MissionTracking({
  missions,
  offersByMission,
  summaries,
  eventsByMission,
  selectedMission,
  onSelectMission,
  showEvents = true,
}) {
  useEffect(() => {
    if (
      missions.length &&
      !missions.some(m => String(m.id) === String(selectedMission))
    ) {
      onSelectMission(String(missions[0].id));
    }
  }, [missions, selectedMission, onSelectMission]);

  const mission = missions.find(
    m => String(m.id) === String(selectedMission)
  );

  const offers = mission ? offersByMission[mission.id] || [] : [];
  const summary = mission ? summaries[mission.id] : null;
  const events = mission ? eventsByMission[mission.id] || [] : [];

  return (
    <section className="panel">
      <SectionTitle
        title="Acompanhamento de missão"
        description="Selecione uma missão para consultar seus dados."
      />

      <Field label="Missão">
        <select
          value={selectedMission}
          onChange={event => onSelectMission(event.target.value)}
        >
          <option value="">Selecione uma missão</option>
          {missions.map(item => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>
      </Field>

      {mission && (
        <>
          <div className="metrics-grid">
            <Metric
              label="Passageiros solicitados"
              value={summary?.pending_seats ?? "—"}
            />
            <Metric
              label="Assentos faltantes"
              value={summary?.missing_seats ?? "—"}
            />
            <Metric
              label="Assentos confirmados"
              value={summary?.confirmed_seats ?? "—"}
            />
            <Metric label="Ofertas recebidas" value={offers.length} />
          </div>

          <h3>Ofertas de naves</h3>

          {offers.length ? (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Nave</th>
                    <th>Assentos</th>
                    <th>Chegada estimada</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {offers.map(offer => (
                    <tr key={offer.id}>
                      <td>{offer.ship_name || offer.ship_id}</td>
                      <td>{offer.offered_seats}</td>
                      <td>{dateTime(offer.arrival_time)}</td>
                      <td><Status value={offer.status} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <Empty title="Nenhuma oferta recebida" />
          )}

          {showEvents && (
            <>
              <h3>Histórico de eventos</h3>

              {events.length ? (
                <div className="timeline">
                  {events.map(event => (
                    <div className="timeline-item" key={event.id}>
                      <i />
                      <div>
                        <b>{event.description || event.event_type}</b>
                        <span>{dateTime(event.created_at)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <Empty title="Nenhum evento registrado" />
              )}
            </>
          )}
        </>
      )}
    </section>
  );
}
