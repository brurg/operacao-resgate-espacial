const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    });
  } catch {
    throw new Error("Não foi possível conectar à API.");
  }

  const raw = await response.text();
  let data = null;
  if (raw) {
    try { data = JSON.parse(raw); } catch { data = raw; }
  }

  if (!response.ok) {
    const detail = data && typeof data === "object" ? data.detail : null;
    throw new Error(detail || `Erro na API (${response.status}).`);
  }
  return data;
}

const json = (method, body) => ({ method, body: JSON.stringify(body) });

export const api = {
  missions: () => request("/missions/"),
  createMission: (data) => request("/missions/", json("POST", data)),
  ships: () => request("/ships/"),
  createShip: (data) => request("/ships/", json("POST", data)),
  offers: (missionId) => request(`/mission-ships/?mission_id=${missionId}`),
  createOffer: (data) => request("/mission-ships/", json("POST", data)),
  requests: () => request("/requests/"),
  respondRequest: (id, confirmedSeats) => request(`/requests/${id}/response`, json("POST", { confirmed_seats: confirmedSeats })),
  cancelRequest: (id) => request(`/requests/${id}/cancel`, { method: "POST" }),
  summary: (missionId) => request(`/requests/mission/${missionId}/summary`),
  events: (missionId) => request(`/missions/${missionId}/events`),
};
