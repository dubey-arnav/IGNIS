import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import FireMap from "../components/map/FireMap";
import FilterBar from "../components/filters/FilterBar";
import EventDetailPanel from "../components/event/EventDetailPanel";

export default function MapPage() {
  const [searchParams] = useSearchParams();
  const [filters, setFilters] = useState({});
  const [selectedEventId, setSelectedEventId] = useState(null);

  useEffect(() => {
    const eventFromUrl = searchParams.get("event");
    if (eventFromUrl) {
      setSelectedEventId(eventFromUrl);
    }
  }, [searchParams]);

  return (
    <div className="map-page">
      <FilterBar filters={filters} onChange={setFilters} />
      <div className="map-page-body">
        <FireMap filters={filters} onSelectEvent={setSelectedEventId} />
        {selectedEventId && (
          <EventDetailPanel
            eventId={selectedEventId}
            onClose={() => setSelectedEventId(null)}
          />
        )}
      </div>
    </div>
  );
}
