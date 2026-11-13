import React from "react";
import { statusClass } from "../constants/status.js";

export function Status({ value }) {
  return (
    <span className={`status status-${statusClass(value)}`}>
      {value || "Não informado"}
    </span>
  );
}

export function Metric({ label, value, description, icon = "✦" }) {
  return (
    <article className="metric-card">
      <div className="metric-top">
        <span>{label}</span>
        <i>{icon}</i>
      </div>
      <strong>{value}</strong>
      {description && <small>{description}</small>}
    </article>
  );
}

export function SectionTitle({
  eyebrow,
  title,
  description,
  action,
}) {
  return (
    <div className="section-title">
      <div>
        {eyebrow && <span className="eyebrow">{eyebrow}</span>}
        <h2>{title}</h2>
        {description && <p>{description}</p>}
      </div>
      {action}
    </div>
  );
}

export function Empty({ title = "Nenhum registro encontrado" }) {
  return (
    <div className="empty-state">
      <strong>{title}</strong>
      <p>Os dados aparecerão aqui quando estiverem disponíveis.</p>
    </div>
  );
}

export function Field({ label, children, hint }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
      {hint && <small>{hint}</small>}
    </label>
  );
}

export function FormActions({
  submitLabel = "Salvar",
  cancelLabel,
  onCancel,
}) {
  return (
    <div className="form-actions">
      {cancelLabel && (
        <button
          type="button"
          className="primary-button"
          onClick={onCancel}
        >
          {cancelLabel}
        </button>
      )}

      <button type="submit" className="primary-button">
        {submitLabel}
      </button>
    </div>
  );
}
