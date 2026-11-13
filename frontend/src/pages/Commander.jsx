import React from "react";

function Commander({ onBack }) {
    return (
      <main className="page-container">
        <header className="page-header">
          <div>
            <h1>Área do Comandante</h1>
            <p>Gerenciamento de naves e solicitações</p>
          </div>
  
          <button className="back-button" onClick={onBack}>
            Voltar
          </button>
        </header>
  
        <nav className="tabs">
          <button>Visão geral</button>
          <button>Disponibilizar nave</button>
          <button>Disponibilidades</button>
          <button>Solicitações</button>
        </nav>
  
        <section className="page-content">
          <h2>Visão geral</h2>
          <p>
            Aqui serão exibidas as disponibilidades e as
            solicitações que precisam de acompanhamento.
          </p>
        </section>
      </main>
    );
  }
  
  export default Commander;