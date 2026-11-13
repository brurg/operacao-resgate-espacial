import React from "react";
import { useEffect } from "react";
import {
  Empty,
  Metric,
  SectionTitle,
  Status,
  Field,
  FormActions,
} from "./Common.jsx";
import { api } from "../services/api.js";
import { dateTime } from "../utils/formatters.js";

export function OperatorOverview({
  missions,
  ships,
  offersByMission,
  summaries,
  eventsByMission,
  selectedMission,
  onSelectMission,
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
    <>
      <SectionTitle
        eyebrow="Painel do operador"
        title="Visão geral"
        description="Acompanhe as missões e os recursos disponíveis para resgate."
      />

      <div className="metrics-grid">
        <Metric label="Missões" value={missions.length} />
        <Metric label="Naves cadastradas" value={ships.length} />
        <Metric
          label="Ofertas de assentos"
          value={Object.values(offersByMission).flat().length}
        />
      </div>

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
                value={summary?.requested_seats ?? "—"}
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
      </section>
    </>
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
                <th>Destino</th>
                <th>Passageiros</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {missions.map(mission => (
                <tr key={mission.id}>
                  <td>{mission.name}</td>
                  <td>{mission.destination}</td>
                  <td>{mission.requested_seats}</td>
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
              <strong>{ship.capacity} assentos</strong>
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

export function CreateMission({ runAction, onDone }) {
  async function handleSubmit(event) {
    event.preventDefault();

    const form = new FormData(event.currentTarget);

    const success = await runAction(
      () =>
        api.createMission({
          name: form.get("name"),
          destination: form.get("destination"),
          requested_seats: Number(form.get("requested_seats")),
        }),
      "Missão cadastrada com sucesso."
    );

    if (success) {
      onDone();
    }
  }

  return (
    <section className="panel form-panel">
      <SectionTitle
        title="Nova missão"
        description="Cadastre uma operação de resgate."
      />

      <form onSubmit={handleSubmit} className="form-grid">
        <Field label="Nome da missão">
          <input name="name" required />
        </Field>

        <Field label="Destino">
          <input name="destination" required />
        </Field>

        <Field label="Passageiros solicitados">
          <input
            name="requested_seats"
            type="number"
            min="1"
            required
          />
        </Field>

        <FormActions submitLabel="Cadastrar missão" />
      </form>
    </section>
  );
}

export function CreateShip({ runAction, onDone }) {
  async function handleSubmit(event) {
    event.preventDefault();

    const form = new FormData(event.currentTarget);

    const success = await runAction(
      () =>
        api.createShip({
          name: form.get("name"),
          capacity: Number(form.get("capacity")),
        }),
      "Nave cadastrada com sucesso."
    );

    if (success) {
      onDone();
    }
  }

  return (
    <section className="panel form-panel">
      <SectionTitle
        title="Cadastrar nave"
        description="Registre uma nova nave na frota."
      />

      <form onSubmit={handleSubmit} className="form-grid">
        <Field label="Nome da nave">
          <input name="name" required />
        </Field>

        <Field label="Capacidade total de assentos">
          <input
            name="capacity"
            type="number"
            min="1"
            required
          />
        </Field>

        <FormActions submitLabel="Cadastrar nave" />
      </form>
    </section>
  );
}
