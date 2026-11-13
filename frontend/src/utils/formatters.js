export function label(value) {
    if (value === null || value === undefined || value === "") {
      return "—";
    }
  
    return value;
}

export function dateTime(value) {
    if (!value) return "—";

return new Date(value).toLocaleString("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
});
}

export function dateInputValue(value) {
    if (!value) return "";

    const date = new Date(value);
    const offset = date.getTimezoneOffset();

    return new Date(date.getTime() - offset * 60000)
        .toISOString()
        .slice(0, 16);
}