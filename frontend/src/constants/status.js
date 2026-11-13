export const STATUS = {
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

export function statusClass(status) {
  const normalized = String(status || "").toUpperCase();

  const classes = {
    CREATED: "created",
    IN_PROGRESS: "in-progress",
    COMPLETED: "completed",
    AVAILABLE: "available",
    REQUESTED: "requested",
    UNAVAILABLE: "unavailable",
    PENDING: "pending",
    CONFIRMED: "confirmed",
    PARTIAL: "partial",
    REFUSED: "refused",
    CANCELLED: "cancelled",
    EXPIRED: "expired",
  };

  return classes[normalized] || "default";
}
  