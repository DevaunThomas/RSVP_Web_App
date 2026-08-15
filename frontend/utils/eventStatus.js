function buildEventDateTime(eventDate, eventTime = "23:59") {
  if (!eventDate) {
    return null;
  }

  const normalizedTime = eventTime || "23:59";
  const eventDateTime = new Date(
    `${eventDate}T${normalizedTime}`
  );

  return Number.isNaN(eventDateTime.getTime())
    ? null
    : eventDateTime;
}

export function isEventPast(
  eventDate,
  eventTime,
  now = new Date()
) {
  const eventDateTime = buildEventDateTime(
    eventDate,
    eventTime
  );

  return eventDateTime
    ? eventDateTime.getTime() < now.getTime()
    : false;
}

export function resolveEventStatus(
  event,
  now = new Date()
) {
  const storedStatus = String(
    event?.status || ""
  ).toLowerCase();

  if (storedStatus === "canceled") {
    return "canceled";
  }

  if (
    isEventPast(
      event?.date,
      event?.startTime,
      now
    )
  ) {
    return "past";
  }

  const capacity = Number(event?.capacity) || 0;
  const rsvpCount = Number(event?.rsvpCount) || 0;

  if (
    storedStatus === "full" ||
    (capacity > 0 && rsvpCount >= capacity)
  ) {
    return "full";
  }

  return "open";
}