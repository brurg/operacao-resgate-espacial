import React, { useEffect } from "react";
import { statusClass, statusLabel } from "../constants/status.js";
import { dateTime } from "../utils/formatters.js";
import { api } from "../services/api.js";

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
          <div className="mission-heading">
            <h3>{mission.name}</h3>
            <Status value={mission.status} />
          </div>

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

function getRequestDetails(request, missions, ships, offersByMission) {
  const mission = missions.find(
    item => String(item.id) === String(request.mission_id)
  );

  const offers = Object.values(offersByMission).flat();

  const offer = offers.find(
    item => String(item.id) === String(request.mission_ship_id)
  );

  const ship = ships.find(
    item => String(item.id) === String(offer?.ship_id)
  );

  return {
    missionName: mission?.name || `Missão ${request.mission_id}`,
    shipName: ship?.name || offer?.ship_name || "Nave não identificada",
  };
}

export function RequestsList({
  requests,
  missions,
  ships,
  offersByMission,
  runAction,
  role,
}) {
  const [confirmedSeats, setConfirmedSeats] = React.useState({});

  async function respond(requestId, seats) {
    await runAction(
      () => api.respondRequest(requestId, seats),
      seats === 0
        ? "Solicitação recusada com sucesso."
        : "Resposta registrada com sucesso."
    );
  }

  async function cancel(requestId) {
    await runAction(
      () => api.cancelRequest(requestId),
      "Solicitação cancelada com sucesso."
    );
  }
  
  const statusOrder = {
    PENDING: 1,
    PARTIAL: 2,
    CONFIRMED: 3,
    UNAVAILABLE: 4,
  };
  
  const sortedRequests = [...requests].sort((a, b) => {
    const orderA = statusOrder[String(a.status).toUpperCase()] ?? 99;
    const orderB = statusOrder[String(b.status).toUpperCase()] ?? 99;
  
    return orderA - orderB;
  });

  return (
    <section className="panel">
      <SectionTitle
        title="Solicitações de resgate"
        description={
          role === "operator"
            ? "Consulte e cancele solicitações pendentes."
            : "Consulte e responda às solicitações recebidas."
        }
      />

      {requests.length ? (
        <div className="request-list">
          {sortedRequests.map(request => {
            const isPending =
              String(request.status).toUpperCase() === "PENDING";

            const seats =
              confirmedSeats[request.id] ??
              String(request.requested_seats);

            const { missionName, shipName } = getRequestDetails(
              request,
              missions,
              ships,
              offersByMission
            );

            return (
              <article className="request-card" key={request.id}>
                <div className="request-main">
                  <h3>{missionName}</h3>
                  <p>{shipName}</p>
                  <p>Prioridade: {request.urgency}</p>
                  <p>
                    {request.requested_seats} assentos solicitados
                  </p>

                  {!isPending && (
                    <p>
                      {request.confirmed_seats ?? 0} assentos confirmados
                    </p>
                  )}

                  <Status value={request.status} />
                </div>

                {isPending && role === "operator" && (
                  <div className="response-controls">
                    <button
                      type="button"
                      className="primary-button"
                      onClick={() => cancel(request.id)}
                    >
                      Cancelar solicitação
                    </button>
                  </div>
                )}

                {isPending && role === "commander" && (
                  <div className="response-controls">
                    <Field label="Assentos a confirmar">
                      <input
                        type="number"
                        min="1"
                        max={request.requested_seats}
                        step="1"
                        value={seats}
                        onChange={event =>
                          setConfirmedSeats(previous => ({
                            ...previous,
                            [request.id]: event.target.value,
                          }))
                        }
                      />
                    </Field>

                    <button
                      type="button"
                      className="primary-button"
                      disabled={
                        seats === "" ||
                        !Number.isInteger(Number(seats)) ||
                        Number(seats) <= 0 ||
                        Number(seats) > request.requested_seats
                      }
                      onClick={() =>
                        respond(request.id, Number(seats))
                      }
                    >
                      Confirmar assentos
                    </button>

                    <button
                      type="button"
                      className="primary-button"
                      onClick={() => respond(request.id, 0)}
                    >
                      Recusar
                    </button>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      ) : (
        <Empty title="Nenhuma solicitação encontrada" />
      )}
    </section>
  );
}