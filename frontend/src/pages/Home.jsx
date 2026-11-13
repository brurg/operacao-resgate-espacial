import React from "react";

export default function Home({ onSelectRole }) {
  return (
    <main className="landing">
      <div className="landing-stars" />

      <div className="landing-inner">
        <div className="landing-symbol">
          <span>✦</span>
        </div>

        <span className="eyebrow">CENTRAL DE OPERAÇÕES</span>

        <h1>
          Operação <span>Resgate Espacial</span>
        </h1>

        <p>
          Organize operações, disponibilize recursos e acompanhe solicitações.
        </p>

        <h2>Selecione seu perfil</h2>

        <div className="profile-grid">
          <button
            type="button"
            className="profile-card"
            onClick={() => onSelectRole("operator")}
          >
            <div className="profile-icon">⌖</div>
            <div className="profile-meta">
              <span>PERFIL 01</span>
              <h3>Operador</h3>
              <p>
                Cadastre e consulte os recursos e acompanhe o andamento das operações.
              </p>
            </div>
            <span className="profile-action">Acessar painel →</span>
          </button>

          <button
            type="button"
            className="profile-card"
            onClick={() => onSelectRole("commander")}
          >
            <div className="profile-icon">✧</div>
            <div className="profile-meta">
              <span>PERFIL 02</span>
              <h3>Comandante</h3>
              <p>
                Disponibilize assentos das naves e gerencie as solicitações recebidas.
              </p>
            </div>
            <span className="profile-action">Acessar painel →</span>
          </button>
        </div>

        <footer className="landing-foot">
          SISTEMA DE GERENCIAMENTO DE RESGATE ESPACIAL
        </footer>
      </div>
    </main>
  );
}
