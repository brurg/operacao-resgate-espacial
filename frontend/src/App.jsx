import React, { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "./services/api.js";

const STATUS = {
  CREATED: "Criada",
  IN_PROGRESS: "Em andamento",
  COMPLETED: "Concluída",
  AVAILABLE: "Disponível",
  REQUESTED: "Solicitada",
  UNAVAILABLE: "Indisponível",
  PENDING: "Pendente",
  CONFIRMED: "Confirmada",
  PARTIAL: "Parcial",
  REFUSED: "Recusada",
  CANCELLED: "Cancelada",
  EXPIRED: "Expirada",
};

function statusClass(value) {
  return String(value || "").toLowerCase().replaceAll("_", "-");
}
function label(value) { return STATUS[value] || value || "—"; }
function dateTime(value) {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("pt-BR");
}
function dateInputValue(date) {
  const d = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return d.toISOString().slice(0, 16);
}

function App() {
  const [role, setRole] = useState(null);
  const [tab, setTab] = useState("overview");
  const [missions, setMissions] = useState([]);
  const [ships, setShips] = useState([]);
  const [requests, setRequests] = useState([]);
  const [offersByMission, setOffersByMission] = useState({});
  const [summaries, setSummaries] = useState({});
  const [eventsByMission, setEventsByMission] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [missionData, shipData, requestData] = await Promise.all([
        api.missions(), api.ships(), api.requests()
      ]);
      setMissions(missionData);
      setShips(shipData);
      setRequests(requestData);

      const offerPairs = await Promise.all(missionData.map(async (mission) => {
        try { return [mission.id, await api.offers(mission.id)]; }
        catch { return [mission.id, []]; }
      }));
      const offerMap = Object.fromEntries(offerPairs);
      setOffersByMission(offerMap);

      const detailPairs = await Promise.all(missionData.map(async (mission) => {
        const [summary, events] = await Promise.all([
          api.summary(mission.id).catch(() => null),
          api.events(mission.id).catch(() => []),
        ]);
        return [mission.id, { summary, events }];
      }));
      const summaryMap = {};
      const eventMap = {};
      detailPairs.forEach(([id, data]) => {
        if (data.summary) summaryMap[id] = data.summary;
        eventMap[id] = data.events;
      });
      setSummaries(summaryMap);
      setEventsByMission(eventMap);
    } catch (err) {
      setError(err.message || "Não foi possível carregar os dados.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const allOffers = useMemo(
    () => Object.values(offersByMission).flat(),
    [offersByMission]
  );

  function enter(nextRole) {
    setRole(nextRole);
    setTab("overview");
    setNotice("");
    setError("");
  }
  function backHome() {
    setRole(null);
    setTab("overview");
    setNotice("");
    setError("");
  }
  function flash(message) {
    setNotice(message);
    setError("");
    window.setTimeout(() => setNotice(""), 4500);
  }
  async function runAction(action, successMessage) {
    setError("");
    setNotice("");
    try {
      await action();
      await refresh();
      flash(successMessage);
    } catch (err) {
      setError(err.message || "A operação não pôde ser concluída.");
    }
  }

  if (!role) {
    return <Home onSelect={enter} loading={loading} error={error} onRefresh={refresh} />;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">✦</div>
          <div><strong>RESGATE</strong><span>OPERAÇÃO ESPACIAL</span></div>
        </div>
        <div className="sidebar-label">ÁREA DE ACESSO</div>
        <div className="role-pill">{role === "operator" ? "◈ Operador" : "✧ Comandante"}</div>
        <div className="sidebar-bottom">
          <button className="sidebar-home" onClick={backHome}>← Voltar ao início</button>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <div className="eyebrow">CENTRO DE CONTROLE / {role === "operator" ? "OPERAÇÕES" : "FROTA"}</div>
            <h1>{role === "operator" ? "Painel do Operador" : "Painel do Comandante"}</h1>
          </div>
          <div className="topbar-actions">
            <button className="icon-button" onClick={refresh} title="Atualizar dados">↻</button>
          </div>
        </header>

        <nav className="tabs app-tabs">
          {(role === "operator"
            ? [["overview","Visão geral"],["missions","Missões"],["new-mission","Cadastrar missão"],["ships","Naves"],["new-ship","Cadastrar nave"]]
            : [["overview","Visão geral"],["offers","Disponibilizar nave"],["fleet","Disponibilidades"],["requests","Solicitações"]]
          ).map(([id, name]) => (
            <button key={id} className={tab === id ? "active" : ""} onClick={() => { setTab(id); setError(""); setNotice(""); }}>{name}</button>
          ))}
        </nav>

        {error && <div className="alert alert-error"><b>Não foi possível concluir:</b> {error}<button onClick={() => setError("")}>×</button></div>}
        {notice && <div className="alert alert-success">{notice}<button onClick={() => setNotice("")}>×</button></div>}
        {loading && <div className="loading-line">Atualizando dados da operação…</div>}

        {role === "operator" && (
          <OperatorArea
            tab={tab} missions={missions} ships={ships} offersByMission={offersByMission}
            summaries={summaries} eventsByMission={eventsByMission} requests={requests}
            runAction={runAction} onTab={setTab}
          />
        )}
        {role === "commander" && (
          <CommanderArea
            tab={tab} missions={missions} ships={ships} offers={allOffers}
            requests={requests} runAction={runAction} onTab={setTab}
          />
        )}
        <footer className="footer">OPERAÇÃO RESGATE ESPACIAL <span>•</span> Centro de coordenação de evacuação</footer>
      </main>
    </div>
  );
}

function Home({ onSelect, loading, error, onRefresh }) {
  return (
    <main className="landing">
      <div className="landing-stars">✦　·　✧　　·　✦</div>
      <div className="landing-inner">
        <div className="landing-symbol">✦</div>
        <div className="eyebrow">CENTRO DE COORDENAÇÃO INTERPLANETÁRIA</div>
        <h1>Operação <span>Resgate</span><br />Espacial</h1>
        <p className="landing-description">Coordenação de missões, frotas e recursos para operações de evacuação espacial.</p>
        <div className="landing-divider"><span /> SELECIONE SEU PERFIL <span /></div>
        <div className="profile-grid">
          <button className="profile-card" onClick={() => onSelect("operator")}>
            <div className="profile-icon">⌘</div>
            <div className="profile-meta">CENTRAL DE OPERAÇÕES</div>
            <h2>Operador</h2>
            <p>Gerencie missões, cadastre naves e acompanhe a evolução das evacuações.</p>
            <span className="profile-action">Acessar painel <b>↗</b></span>
          </button>
          <button className="profile-card" onClick={() => onSelect("commander")}>
            <div className="profile-icon">✧</div>
            <div className="profile-meta">GESTÃO DE FROTA</div>
            <h2>Comandante</h2>
            <p>Disponibilize assentos de suas naves e responda às solicitações de resgate.</p>
            <span className="profile-action">Acessar painel <b>↗</b></span>
          </button>
        </div>
        {error && <div className="home-error">{error} <button onClick={onRefresh}>Tentar novamente</button></div>}
      </div>
    </main>
  );
}

function Metric({ label: title, value, detail, icon }) {
  return <div className="metric-card"><div className="metric-top"><span>{title}</span><i>{icon}</i></div><strong>{value}</strong><small>{detail}</small></div>;
}
function SectionTitle({ title, subtitle, action }) {
  return <div className="section-title"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>{action}</div>;
}
function Empty({ children = "Nenhum registro encontrado." }) {
  return <div className="empty-state"><span>◇</span><p>{children}</p></div>;
}
function Status({ value }) {
  return <span className={`status status-${statusClass(value)}`}>{label(value)}</span>;
}
function Field({ label: title, children, hint }) {
  return <label className="field"><span>{title}</span>{children}{hint && <small>{hint}</small>}</label>;
}
function FormActions({ children }) { return <div className="form-actions">{children}</div>; }

function OperatorArea({ tab, missions, ships, offersByMission, summaries, eventsByMission, requests, runAction, onTab }) {
  const [selectedMission, setSelectedMission] = useState("");
  useEffect(() => {
    if (missions.length && !missions.some(m => String(m.id) === String(selectedMission))) setSelectedMission(String(missions[0].id));
  }, [missions, selectedMission]);
  const current = missions.find(m => String(m.id) === String(selectedMission));
  const offers = current ? (offersByMission[current.id] || []) : [];
  const summary = current ? summaries[current.id] : null;
  const currentRequests = current ? requests.filter(r => r.mission_id === current.id) : [];
  const events = current ? (eventsByMission[current.id] || []) : [];

  if (tab === "new-mission") return <CreateMission runAction={runAction} onDone={() => onTab("missions")} />;
  if (tab === "new-ship") return <CreateShip runAction={runAction} onDone={() => onTab("ships")} />;
  if (tab === "ships") return <ShipsList ships={ships} />;
  if (tab === "missions") return <MissionsList missions={missions} onSelect={(id) => { setSelectedMission(String(id)); onTab("overview"); }} />;

  return (
    <>
      <section className="welcome-row">
        <div><div className="eyebrow">RESUMO DA OPERAÇÃO</div><h2>Visão geral</h2><p>Acompanhe os recursos e o andamento das missões cadastradas.</p></div>
        <div className="welcome-chip">✦ Coordenação ativa</div>
      </section>
      <div className="metrics-grid">
        <Metric label="Missões cadastradas" value={missions.length} detail="Total de operações" icon="◎" />
        <Metric label="Naves na frota" value={ships.length} detail="Naves registradas" icon="⌁" />
        <Metric label="Assentos confirmados" value={Object.values(summaries).reduce((n,s) => n + s.confirmed_seats, 0)} detail="Em todas as missões" icon="✓" />
        <Metric label="Solicitações pendentes" value={requests.filter(r => r.status === "PENDING").length} detail="Aguardando resposta" icon="◷" />
      </div>
      <section className="panel">
        <SectionTitle title="Acompanhamento de missão" subtitle="Selecione uma missão para consultar os recursos, assentos e eventos." />
        {missions.length === 0 ? <Empty>Cadastre uma missão para começar a acompanhar as operações.</Empty> : <>
          <Field label="Missão selecionada">
            <select value={selectedMission} onChange={e => setSelectedMission(e.target.value)}>
              {missions.map(m => <option key={m.id} value={m.id}>#{m.id} — {m.station}</option>)}
            </select>
          </Field>
          {current && <div className="mission-overview">
            <div className="mission-heading"><div><span className="eyebrow">MISSÃO #{current.id}</span><h3>{current.station}</h3><p>{current.people_count} pessoas aguardando evacuação</p></div><Status value={current.status} /></div>
            <div className="seat-progress">
              <div className="progress-label"><span>Assentos confirmados</span><b>{summary?.confirmed_seats || 0} / {current.people_count}</b></div>
              <div className="progress-track"><span style={{width: `${Math.min(100, ((summary?.confirmed_seats || 0) / current.people_count) * 100)}%`}} /></div>
              <div className="progress-legend"><span>{summary?.pending_seats || 0} pendentes</span><span>{summary?.missing_seats ?? current.people_count} ainda necessários</span></div>
            </div>
            <div className="mini-stats">
              <div><b>{offers.length}</b><span>Disponibilidades</span></div>
              <div><b>{currentRequests.length}</b><span>Solicitações</span></div>
              <div><b>{summary?.uncommitted_seats ?? current.people_count}</b><span>Assentos não comprometidos</span></div>
            </div>
          </div>}
        </>}
      </section>
      {current && <div className="two-columns">
        <section className="panel">
          <SectionTitle title="Naves disponibilizadas" subtitle={`Recursos vinculados à missão #${current.id}`} />
          {offers.length === 0 ? <Empty>Nenhuma nave disponibilizada para esta missão.</Empty> :
            <div className="table-wrap"><table><thead><tr><th>Nave</th><th>Assentos</th><th>Chegada estimada</th><th>Status</th></tr></thead><tbody>
              {offers.map(o => <tr key={o.id}><td>#{o.ship_id} — {ships.find(s => s.id === o.ship_id)?.name || "Nave"}</td><td>{o.offered_seats}</td><td>{dateTime(o.arrival_time)}</td><td><Status value={o.status} /></td></tr>)}
            </tbody></table></div>}
        </section>
        <section className="panel">
          <SectionTitle title="Linha do tempo" subtitle="Eventos registrados nesta missão" />
          {events.length === 0 ? <Empty>Nenhum evento registrado até o momento.</Empty> :
            <div className="timeline">{[...events].reverse().slice(0,6).map(ev => <div className="timeline-item" key={ev.id}><i /><div><b>{ev.description}</b><span>{dateTime(ev.timestamp)}</span></div></div>)}</div>}
        </section>
      </div>}
    </>
  );
}

function CreateMission({ runAction, onDone }) {
  const [station, setStation] = useState("");
  const [people, setPeople] = useState("1");
  return <section className="panel form-panel"><SectionTitle title="Cadastrar missão" subtitle="Registre uma nova operação de evacuação." />
    <form onSubmit={e => { e.preventDefault(); runAction(() => api.createMission({station: station.trim(), people_count: Number(people)}), "Missão cadastrada com sucesso."); onDone(); }}>
      <div className="form-grid">
        <Field label="Estação / Local de resgate"><input required value={station} onChange={e => setStation(e.target.value)} placeholder="Ex.: Estação Europa-7" /></Field>
        <Field label="Quantidade de pessoas"><input required type="number" min="1" step="1" value={people} onChange={e => setPeople(e.target.value)} /></Field>
      </div>
      <FormActions><button className="primary-button" type="submit">+ Cadastrar missão</button></FormActions>
    </form>
  </section>;
}
function CreateShip({ runAction, onDone }) {
  const [name, setName] = useState("");
  const [capacity, setCapacity] = useState("1");
  return <section className="panel form-panel"><SectionTitle title="Cadastrar nave" subtitle="Adicione uma nave à frota disponível para as operações." />
    <form onSubmit={e => { e.preventDefault(); runAction(() => api.createShip({name: name.trim(), total_capacity: Number(capacity)}), "Nave cadastrada com sucesso."); onDone(); }}>
      <div className="form-grid">
        <Field label="Nome da nave"><input required value={name} onChange={e => setName(e.target.value)} placeholder="Ex.: Aurora-01" /></Field>
        <Field label="Capacidade total de assentos"><input required type="number" min="1" step="1" value={capacity} onChange={e => setCapacity(e.target.value)} /></Field>
      </div>
      <FormActions><button className="primary-button" type="submit">+ Cadastrar nave</button></FormActions>
    </form>
  </section>;
}
function MissionsList({ missions, onSelect }) {
  return <section className="panel"><SectionTitle title="Missões cadastradas" subtitle="Consulte as operações e abra o acompanhamento detalhado." />
    {missions.length === 0 ? <Empty>Nenhuma missão cadastrada. Comece criando uma nova missão.</Empty> :
      <div className="table-wrap"><table><thead><tr><th>ID</th><th>Estação</th><th>Pessoas</th><th>Status</th><th>Criação</th><th /></tr></thead><tbody>
        {missions.map(m => <tr key={m.id}><td>#{m.id}</td><td><b>{m.station}</b></td><td>{m.people_count}</td><td><Status value={m.status} /></td><td>{dateTime(m.created_at)}</td><td><button className="text-button" onClick={() => onSelect(m.id)}>Acompanhar →</button></td></tr>)}
      </tbody></table></div>}
  </section>;
}
function ShipsList({ ships }) {
  return <section className="panel"><SectionTitle title="Frota cadastrada" subtitle="Naves registradas no sistema e suas capacidades." />
    {ships.length === 0 ? <Empty>Nenhuma nave cadastrada.</Empty> :
      <div className="ship-grid">{ships.map(s => <div className="ship-card" key={s.id}><div className="ship-card-icon">⌁</div><div><span className="eyebrow">NAVE #{s.id}</span><h3>{s.name}</h3><p>Capacidade total</p><strong>{s.total_capacity} <small>assentos</small></strong></div></div>)}</div>}
  </section>;
}

function CommanderArea({ tab, missions, ships, offers, requests, runAction, onTab }) {
  const [missionId, setMissionId] = useState("");
  const [shipId, setShipId] = useState("");
  const [seats, setSeats] = useState("1");
  const [arrival, setArrival] = useState(dateInputValue(new Date(Date.now() + 60 * 60 * 1000)));
  const [responses, setResponses] = useState({});
  useEffect(() => {
    if (missions.length && !missions.some(m => String(m.id) === String(missionId))) setMissionId(String(missions.find(m => m.status === "CREATED")?.id || missions[0].id));
  }, [missions, missionId]);
  useEffect(() => {
    if (ships.length && !ships.some(s => String(s.id) === String(shipId))) setShipId(String(ships[0].id));
  }, [ships, shipId]);
  const selectedShip = ships.find(s => String(s.id) === String(shipId));
  const pending = requests.filter(r => r.status === "PENDING");

  if (tab === "offers") return <section className="panel form-panel"><SectionTitle title="Disponibilizar nave" subtitle="Informe a missão, a nave, a quantidade de assentos e o horário estimado de chegada." />
    {missions.length === 0 || ships.length === 0 ? <Empty>É necessário haver ao menos uma missão e uma nave cadastradas para disponibilizar assentos.</Empty> :
      <form onSubmit={e => { e.preventDefault(); runAction(() => api.createOffer({mission_id: Number(missionId), ship_id: Number(shipId), offered_seats: Number(seats), arrival_time: new Date(arrival).toISOString()}), "Disponibilidade registrada com sucesso."); }}>
        <div className="form-grid">
          <Field label="Missão">
            <select required value={missionId} onChange={e => setMissionId(e.target.value)}>
              {missions.map(m => <option key={m.id} value={m.id} disabled={m.status !== "CREATED"}>#{m.id} — {m.station} ({label(m.status)})</option>)}
            </select>
          </Field>
          <Field label="Nave">
            <select required value={shipId} onChange={e => setShipId(e.target.value)}>
              {ships.map(s => <option key={s.id} value={s.id}>#{s.id} — {s.name} / {s.total_capacity} assentos</option>)}
            </select>
          </Field>
          <Field label="Quantidade de assentos oferecidos" hint={selectedShip ? `Capacidade total da nave: ${selectedShip.total_capacity}` : ""}>
            <input type="number" min="1" max={selectedShip?.total_capacity || undefined} required value={seats} onChange={e => setSeats(e.target.value)} />
          </Field>
          <Field label="Previsão de chegada">
            <input type="datetime-local" required value={arrival} onChange={e => setArrival(e.target.value)} />
          </Field>
        </div>
        <div className="form-note">A API permite disponibilizar naves apenas para missões com status “Criada”. Uma mesma nave não pode ser disponibilizada duas vezes para a mesma missão.</div>
        <FormActions><button className="primary-button" type="submit">＋ Confirmar disponibilidade</button></FormActions>
      </form>}
  </section>;

  if (tab === "fleet") return <section className="panel"><SectionTitle title="Disponibilidades registradas" subtitle="Naves oferecidas para cada missão e previsão de chegada." />
    {offers.length === 0 ? <Empty>Ainda não há disponibilidades registradas.</Empty> :
      <div className="table-wrap"><table><thead><tr><th>Missão</th><th>Nave</th><th>Assentos</th><th>Chegada estimada</th><th>Status</th></tr></thead><tbody>
        {offers.map(o => <tr key={o.id}><td>#{o.mission_id} — {missions.find(m => m.id === o.mission_id)?.station || "Missão"}</td><td>#{o.ship_id} — {ships.find(s => s.id === o.ship_id)?.name || "Nave"}</td><td>{o.offered_seats}</td><td>{dateTime(o.arrival_time)}</td><td><Status value={o.status} /></td></tr>)}
      </tbody></table></div>}
  </section>;

  if (tab === "requests") return <section className="panel"><SectionTitle title="Solicitações de resgate" subtitle="Analise os pedidos recebidos e informe quantos assentos podem ser confirmados." />
    {requests.length === 0 ? <Empty>Nenhuma solicitação recebida. As solicitações serão exibidas aqui quando forem geradas pelo processo de seleção de naves.</Empty> :
      <div className="request-list">{requests.map(r => {
        const offer = offers.find(o => o.id === r.mission_ship_id);
        const mission = missions.find(m => m.id === r.mission_id);
        const ship = ships.find(s => s.id === offer?.ship_id);
        return <div className="request-card" key={r.id}>
          <div className="request-main">
            <div><span className="eyebrow">SOLICITAÇÃO #{r.id} · MISSÃO #{r.mission_id}</span><h3>{mission?.station || "Missão"} <span>·</span> {ship?.name || `Oferta #${r.mission_ship_id}`}</h3><p>{r.requested_seats} assentos solicitados · Criada em {dateTime(r.created_at)}</p></div>
            <Status value={r.status} />
          </div>
          {r.status === "PENDING" ? <div className="response-controls">
            <Field label="Assentos que podem ser confirmados">
              <input type="number" min="0" max={r.requested_seats} value={responses[r.id] ?? String(r.requested_seats)} onChange={e => setResponses(prev => ({...prev, [r.id]: e.target.value}))} />
            </Field>
            <button className="primary-button" onClick={() => runAction(() => api.respondRequest(r.id, Number(responses[r.id] ?? r.requested_seats)), "Resposta registrada com sucesso.")}>Enviar resposta</button>
          </div> : <div className="request-result">Confirmados: <b>{r.confirmed_seats}</b> de {r.requested_seats} assentos</div>}
          {r.expires_at && <small className="muted-line">Prazo de resposta: {dateTime(r.expires_at)}</small>}
        </div>;
      })}</div>}
  </section>;

  return <>
    <section className="welcome-row">
      <div><div className="eyebrow">GESTÃO DE RECURSOS</div><h2>Visão geral da frota</h2><p>Disponibilize a capacidade das naves e acompanhe as solicitações de resgate.</p></div>
      <div className="welcome-chip">✧ Frota espacial</div>
    </section>
    <div className="metrics-grid">
      <Metric label="Naves cadastradas" value={ships.length} detail="Frota disponível no sistema" icon="⌁" />
      <Metric label="Missões abertas" value={missions.filter(m => m.status === "CREATED").length} detail="Aceitam novas disponibilidades" icon="◎" />
      <Metric label="Disponibilidades" value={offers.length} detail="Ofertas registradas" icon="✧" />
      <Metric label="Solicitações pendentes" value={pending.length} detail="Aguardando sua resposta" icon="◷" />
    </div>
    <div className="two-columns">
      <section className="panel">
        <SectionTitle title="Ações rápidas" subtitle="Gerencie os recursos da frota." />
        <button className="action-tile" onClick={() => onTab("offers")}><span>＋</span><div><b>Disponibilizar uma nave</b><small>Ofereça assentos para uma missão</small></div><i>→</i></button>
        <button className="action-tile" onClick={() => onTab("requests")}><span>⇄</span><div><b>Responder solicitações</b><small>Confirme total ou parcialmente os assentos</small></div><i>→</i></button>
      </section>
      <section className="panel">
        <SectionTitle title="Solicitações recentes" subtitle="Pedidos que aguardam resposta." />
        {pending.length === 0 ? <Empty>Nenhuma solicitação pendente.</Empty> : pending.slice(0,4).map(r => <div className="recent-request" key={r.id}><div><b>Solicitação #{r.id}</b><span>Missão #{r.mission_id} · {r.requested_seats} assentos</span></div><Status value={r.status} /></div>)}
      </section>
    </div>
    <div className="info-banner"><b>Como funciona:</b> disponibilize assentos para uma missão. Quando a estratégia de seleção criar uma solicitação, ela aparecerá na aba “Solicitações” para que você informe a quantidade que consegue confirmar.</div>
  </>;
}

export default App;
