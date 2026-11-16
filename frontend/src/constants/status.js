export const STATUS_LABELS = {
  CREATED: "Criada",
  IN_PROGRESS: "Em andamento",
  COMPLETED: "Concluída",
  AVAILABLE: "Disponível",
  REQUESTED: "Solicitada",
  UNAVAILABLE: "Indisponível",
  PENDING: "Pendente",
  CONFIRMED: "Confirmada",
  PARTIAL: "Parcial",
  CANCELLED: "Cancelada",
  EXPIRED: "Expirada",
};

export function statusClass(value) {
  return String(value || "").toLowerCase().replaceAll("_", "-");
}

export function statusLabel(value) {
  return STATUS_LABELS[String(value || "").toUpperCase()] || value || "Não informado";
}