import React from "react";

function Operator({ onBack }) {
    return (
      <main className="page-container">
        <header className="page-header">
          <div>
            <h1>Área do Operador</h1>
            <p>Gerenciamento das operações espaciais</p>
          </div>
  
          <button className="back-button" onClick={onBack}>
            Voltar
          </button>
        </header>
  
        <nav className="tabs">
          <button>Visão geral</button>
          <button>Cadastrar missão</button>
          <button>Cadastrar nave</button>
          <button>Missões</button>
          <button>Naves</button>
        </nav>
  
        <section className="page-content">
          <h2>Visão geral</h2>
          <p>
            Aqui serão exibidos os indicadores e o acompanhamento
            das missões cadastradas.
          </p>
        </section>
      </main>
    );
  }
  
  export default Operator;