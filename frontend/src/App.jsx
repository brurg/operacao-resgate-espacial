
import React, { useCallback, useEffect, useState } from "react";
import { api } from "./services/api.js";

import Home from "./pages/Home.jsx";
import OperatorArea from "./pages/Operator.jsx";
import CommanderArea from "./pages/Commander.jsx";

export default function App() {
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
        api.missions(),
        api.ships(),
        api.requests(),
      ]);

      setMissions(missionData);
      setShips(shipData);
      setRequests(requestData);

      const results = await Promise.all(
        missionData.map(async mission => {
          const [offersResult, summaryResult, eventsResult] =
            await Promise.allSettled([
              api.offers(mission.id),
              api.summary(mission.id),
              api.events(mission.id),
            ]);

          return {
            id: mission.id,
            offers:
              offersResult.status === "fulfilled"
                ? offersResult.value
                : [],
            summary:
              summaryResult.status === "fulfilled"
                ? summaryResult.value
                : null,
            events:
              eventsResult.status === "fulfilled"
                ? eventsResult.value
                : [],
          };
        })
      );

      const offers = {};
      const summariesData = {};
      const events = {};

      results.forEach(result => {
        offers[result.id] = result.offers;
        summariesData[result.id] = result.summary;
        events[result.id] = result.events;
      });

      setOffersByMission(offers);
      setSummaries(summariesData);
      setEventsByMission(events);

      return true;
    } catch (err) {
      setError(err.message || "Não foi possível carregar os dados.");
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function runAction(action, successMessage) {
    setError("");
    setNotice("");

    try {
      await action();

      const refreshed = await refresh();

      if (!refreshed) {
        return false;
      }

      setNotice(successMessage);
      return true;
    } catch (err) {
      setError(err.message || "Não foi possível executar a operação.");
      return false;
    }
  }

  function selectRole(selectedRole) {
    setRole(selectedRole);
    setTab("overview");
    setError("");
    setNotice("");
  }

  function logout() {
    setRole(null);
    setTab("overview");
    setError("");
    setNotice("");
  }

  if (!role) {
    return <Home onSelectRole={selectRole} />;
  }

  const sharedProps = {
    tab,
    onTab: setTab,
    missions,
    ships,
    requests,
    offersByMission,
    summaries,
    eventsByMission,
    loading,
    error,
    notice,
    refresh,
    runAction,
    onLogout: logout,
  };

  return role === "operator" ? (
    <OperatorArea {...sharedProps} />
  ) : (
    <CommanderArea {...sharedProps} />
  );
}
