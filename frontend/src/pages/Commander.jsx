import React, { useState } from "react";
import {
  CommanderOverview,
  CreateOffer,
  FleetList,
  RequestsList,
} from "../components/Commander.jsx";
import { MissionsList } from "../components/Common.jsx";

const TABS = [
  { id: "overview", label: "Visão geral" },
  { id: "missions", label: "Missões" },
  { id: "offers", label: "Disponibilizar assentos" },
  { id: "fleet", label: "Disponibilidades" },
  { id: "requests", label: "Solicitações" },
];

export default function CommanderArea(props) {
  const [selectedMission, setSelectedMission] = useState("");

  function selectMission(id) {
    setSelectedMission(String(id));
    props.onTab("overview");
  }

  function renderContent() {
    switch (props.tab) {
      case "offers":
        return (
          <CreateOffer
            missions={props.missions}
            ships={props.ships}
            runAction={props.runAction}
            onDone={() => props.onTab("fleet")}
          />
        );

      case "fleet":
        return (
          <FleetList
            ships={props.ships}
            offersByMission={props.offersByMission}
          />
        );

      case "requests":
        return (
          <RequestsList
            requests={props.requests}
            missions={props.missions}
            ships={props.ships}
            offersByMission={props.offersByMission}
            runAction={props.runAction}
          />
        );

      case "missions":
        return (
          <MissionsList
            missions={props.missions}
            onSelect={selectMission}
          />
        );

      default:
        return (
          <CommanderOverview
            missions={props.missions}
            ships={props.ships}
            requests={props.requests}
            offersByMission={props.offersByMission}
            summaries={props.summaries}
            eventsByMission={props.eventsByMission}
            selectedMission={selectedMission}
            selectMission={setSelectedMission}
          />
        );
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div>
            <strong>RESGATE</strong>
            <small>OPERAÇÃO ESPACIAL</small>
          </div>
        </div>

        <span className="sidebar-label">PERFIL ATUAL</span>
        <div className="role-pill">Comandante</div>

        <span className="sidebar-label">MENU PRINCIPAL</span>

        <nav className="app-tabs">
          {TABS.map(item => (
            <button
              key={item.id}
              type="button"
              className={props.tab === item.id ? "active" : ""}
              onClick={() => props.onTab(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom" />
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <span className="eyebrow">CENTRAL DE CONTROLE</span>
            <h1>Área do Comandante</h1>
          </div>

          <div className="topbar-actions">
            <button
              type="button"
              className="refresh-button"
              onClick={props.refresh}
              disabled={props.loading}
              title="Atualizar dados"
              aria-label="Atualizar dados"
            >
              <span
                className={
                  props.loading
                    ? "refresh-icon spinning"
                    : "refresh-icon"
                }
              >
                ↻
              </span>
            </button>

            <button
              type="button"
              className="back-button"
              onClick={props.onLogout}
            >
              ← Voltar
            </button>
          </div>
        </header>

        <div className="page-content">
          {props.error && (
            <div className="alert">
              {props.error}
            </div>
          )}

          {props.notice && (
            <div className="info-banner">
              {props.notice}
            </div>
          )}

          {renderContent()}
        </div>
      </main>
    </div>
  );
}