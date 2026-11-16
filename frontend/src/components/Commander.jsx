import React from "react";
import {
  Empty,
  Metric,
  SectionTitle,
  Status,
  Field,
  FormActions,
  MissionTracking
} from "./Common.jsx";
import { api } from "../services/api.js";
import { dateTime } from "../utils/formatters.js";

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
    shipName: ship?.name || offer?.ship_name || "Nave não identificada"
  };
}

export function CommanderOverview({
  missions,
  ships,
  requests,
  offersByMission,
  summaries,
  eventsByMission,
  selectedMission,
  selectMission
}) {
  const pendingRequests = requests.filter(
    request => String(request.status).toUpperCase() === "PENDING"
  );

  const totalOffers = Object.values(offersByMission).flat().length;

  return (
    <>
      <SectionTitle
        eyebrow="Painel do comandante"
        title="Visão geral"
        description="Gerencie a disponibilidade da frota e as solicitações de resgate."
      />

      <div className="metrics-grid">
        <Metric label="Missões ativas" value={missions.filter(mission => mission.status !== "COMPLETED").length} />
        <Metric label="Naves cadastradas" value={ships.length} />
        <Metric label="Ofertas realizadas" value={totalOffers} />
        <Metric
          label="Solicitações pendentes"
          value={pendingRequests.length}
        />
      </div>

      <section className="panel">
        <SectionTitle title="Solicitações pendentes" />

        {pendingRequests.length ? (
          <div className="request-list">
            {pendingRequests.map(request => {
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

                    <span>
                      {request.requested_seats} assentos solicitados
                    </span>
                  </div>

                  <Status value={request.status} />
                </article>
              );
            })}
          </div>
        ) : (
          <Empty title="Nenhuma solicitação pendente" />
        )}
      </section>

      <MissionTracking
        missions={missions}
        offersByMission={offersByMission}
        summaries={summaries}
        eventsByMission={eventsByMission}
        selectedMission={selectedMission}
        onSelectMission={selectMission}
        showEvents={false}
      />
    </>
  );
}

export function CreateOffer({
  missions,
  ships,
  runAction,
  onDone,
}) {
  async function handleSubmit(event) {
    event.preventDefault();

    const form = new FormData(event.currentTarget);

    const success = await runAction(
      () =>
        api.createOffer({
          mission_id: Number(form.get("mission_id")),
          ship_id: Number(form.get("ship_id")),
          offered_seats: Number(form.get("offered_seats")),
          arrival_time: form.get("arrival_time"),
        }),
      "Disponibilidade enviada com sucesso."
    );

    if (success) {
      onDone();
    }
  }

  return (
    <section className="panel form-panel">
      <SectionTitle
        title="Disponibilizar assentos"
        description="Informe a missão, a nave, a quantidade de assentos e a previsão de chegada."
      />

      <form onSubmit={handleSubmit} className="form-grid">
        <Field label="Missão">
          <select name="mission_id" required defaultValue="">
            <option value="" disabled>Selecione uma missão</option>
            {missions.map(mission => (
              <option key={mission.id} value={mission.id}>
                {mission.name}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Nave">
          <select name="ship_id" required defaultValue="">
            <option value="" disabled>Selecione uma nave</option>
            {ships.map(ship => (
              <option key={ship.id} value={ship.id}>
                {ship.name}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Assentos disponibilizados">
          <input
            name="offered_seats"
            type="number"
            min="1"
            step="1"
            required
          />
        </Field>

        <Field label="Previsão de chegada">
          <input
            name="arrival_time"
            type="datetime-local"
            required
          />
        </Field>

        <FormActions submitLabel="Enviar disponibilidade" />
      </form>
    </section>
  );
}

export function FleetList({ ships, offersByMission }) {
  const offers = Object.values(offersByMission).flat();

  return (
    <section className="panel">
      <SectionTitle
        title="Disponibilidade da frota"
        description="Consulte as ofertas de assentos enviadas para as missões."
      />

      {offers.length ? (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Nave</th>
                <th>Missão</th>
                <th>Assentos</th>
                <th>Chegada estimada</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {offers.map(offer => {
                const ship = ships.find(
                  item => String(item.id) === String(offer.ship_id)
                );

                return (
                  <tr key={offer.id}>
                    <td>{ship?.name || offer.ship_id}</td>
                    <td>{offer.mission_name || offer.mission_id}</td>
                    <td>{offer.offered_seats}</td>
                    <td>{dateTime(offer.arrival_time)}</td>
                    <td><Status value={offer.status} /></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <Empty title="Nenhuma disponibilidade enviada" />
      )}
    </section>
  );
}

export function RequestsList({
  requests,
  missions,
  ships,
  offersByMission,
  runAction
}) {
  const [confirmedSeats, setConfirmedSeats] = React.useState({});

  async function respond(requestId, seats) {
    await runAction(
      () => api.respondRequest(requestId, seats),
      "Resposta registrada com sucesso."
    );
  }

  return (
    <section className="panel">
      <SectionTitle
        title="Solicitações de resgate"
        description="Consulte e responda às solicitações recebidas."
      />

      {requests.length ? (
        <div className="request-list">
          {requests.map(request => {
            const isPending =
              String(request.status).toUpperCase() === "PENDING";

            const seats =
              confirmedSeats[request.id] ?? String(request.requested_seats);
            
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

                  <p>
                    {request.requested_seats} assentos solicitados
                  </p>

                  {!isPending && (
                    <p>
                      {request.confirmed_seats} assentos confirmados
                    </p>
                  )}

                  <Status value={request.status} />
                </div>

                {isPending && (
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
                            [request.id]: event.target.value
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
                      onClick={() => respond(request.id, Number(seats))}
                    >
                      Enviar resposta
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
        <Empty title="Nenhuma solicitação recebida" />
      )}
    </section>
  );
}