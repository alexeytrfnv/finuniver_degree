export const formatDate = (date: Date) => {
  const d = new Date(date)

  const options: Intl.DateTimeFormatOptions = {
    day: "numeric", // 27
    month: "long", // февраля
    hour: "2-digit", // 10
    minute: "2-digit", // 42
    hour12: false, // 24‑часовой формат, без «AM/PM»
  }

  const formatted = new Intl.DateTimeFormat("ru-RU", options).format(d)

  return formatted
}
