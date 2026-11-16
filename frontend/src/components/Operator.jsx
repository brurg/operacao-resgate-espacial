import React from "react";
import {
  Metric,
  SectionTitle,
  Field,
  FormActions,
  MissionTracking
} from "./Common.jsx";
import { api } from "../services/api.js";

export function OperatorOverview({
  missions,
  ships,
  offersByMission,
  summaries,
  eventsByMission,
  selectedMission,
  onSelectMission,
}) {
  const totalOffers = Object.values(offersByMission).flat().length;

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
        <Metric label="Ofertas de assentos" value={totalOffers} />
      </div>

      <MissionTracking
        missions={missions}
        offersByMission={offersByMission}
        summaries={summaries}
        eventsByMission={eventsByMission}
        selectedMission={selectedMission}
        onSelectMission={onSelectMission}
      />
    </>
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
          station: form.get("station"),
          people_count: Number(form.get("requested_seats")),
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

        <Field label="Estação">
          <input name="station" required />
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
          total_capacity: Number(form.get("total_capacity")),
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
            name="total_capacity"
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
