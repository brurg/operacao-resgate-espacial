import React, { useState } from "react";
import {
  OperatorOverview,
  CreateMission,
  CreateShip,
} from "../components/Operator.jsx";
import {
  ShipsList,
  MissionsList,
  RequestsList,
} from "../components/Common.jsx";

const TABS = [
  { id: "overview", label: "Visão geral" },
  { id: "missions", label: "Missões" },
  { id: "requests", label: "Solicitações" },
  { id: "create-mission", label: "Cadastrar missão" },
  { id: "create-ship", label: "Cadastrar nave" },
  { id: "ships", label: "Naves" },
];

export default function OperatorArea(props) {
  const [selectedMission, setSelectedMission] = useState("");

  function selectMission(id) {
    setSelectedMission(String(id));
    props.onTab("overview");
  }

  function renderContent() {
    switch (props.tab) {
      case "create-mission":
        return (
          <CreateMission
            runAction={props.runAction}
            onDone={() => props.onTab("missions")}
          />
        );

      case "create-ship":
        return (
          <CreateShip
            runAction={props.runAction}
            onDone={() => props.onTab("ships")}
          />
        );

      case "missions":
        return (
          <MissionsList
            missions={props.missions}
            onSelect={selectMission}
          />
        );

      case "ships":
        return <ShipsList ships={props.ships} />;

      case "requests":
        return (
          <RequestsList
            requests={props.requests}
            missions={props.missions}
            ships={props.ships}
            offersByMission={props.offersByMission}
            runAction={props.runAction}
            role="operator"
          />
        );

      default:
        return (
          <OperatorOverview
            missions={props.missions}
            ships={props.ships}
            offersByMission={props.offersByMission}
            summaries={props.summaries}
            eventsByMission={props.eventsByMission}
            selectedMission={selectedMission}
            onSelectMission={setSelectedMission}
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
        <div className="role-pill">Operador</div>

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
            <h1>Área do Operador</h1>
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
              <span className={props.loading ? "refresh-icon spinning" : "refresh-icon"}>
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