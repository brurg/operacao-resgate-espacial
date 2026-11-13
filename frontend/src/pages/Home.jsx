import React from "react";

function Home({ onSelectOperator, onSelectCommander }) {
    return (
      <main className="home-container">
        <div className="home-content">
          <h1>Operação Resgate Espacial</h1>
  
          <p>
            Sistema de gerenciamento de missões de evacuação espacial.
          </p>
  
          <h2>Selecione seu perfil</h2>
  
          <div className="role-container">
            <button
              className="role-card"
              onClick={onSelectOperator}
            >
              <span className="role-icon">🛰️</span>
              <h3>Operador</h3>
              <p>
                Gerencie missões, cadastre naves e acompanhe
                o andamento das operações.
              </p>
            </button>
  
            <button
              className="role-card"
              onClick={onSelectCommander}
            >
              <span className="role-icon">🚀</span>
              <h3>Comandante</h3>
              <p>
                Disponibilize naves e gerencie as solicitações
                de assentos recebidas.
              </p>
            </button>
          </div>
        </div>
      </main>
    );
  }
  
  export default Home;