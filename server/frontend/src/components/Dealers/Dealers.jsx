import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

import "./Dealers.css";
import "../assets/style.css";
import Header from "../Header/Header";
import review_icon from "../assets/reviewicon.png";

const Dealers = () => {
  const [dealersList, setDealersList] = useState([]);
  const [states, setStates] = useState([]);

  const { state } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    const loadDealers = async () => {
      try {
        // Get all dealers first to populate the State dropdown
        const allResponse = await fetch("/djangoapp/get_dealers");
        const allData = await allResponse.json();

        if (allData.status === 200) {
          const allDealers = Array.from(allData.dealers);

          const uniqueStates = Array.from(
            new Set(allDealers.map((dealer) => dealer.state))
          );

          setStates(uniqueStates);

          // No state selected -> display all dealers
          if (!state || state === "All") {
            setDealersList(allDealers);
            return;
          }
        }

        // State selected -> fetch only dealers from that state
        const stateResponse = await fetch(
          `/djangoapp/get_dealers/${state}`
        );

        const stateData = await stateResponse.json();

        if (stateData.status === 200) {
          setDealersList(Array.from(stateData.dealers));
        }
      } catch (error) {
        console.error("Error loading dealerships:", error);
      }
    };

    loadDealers();
  }, [state]);

  const filterDealers = (selectedState) => {
    if (selectedState === "All") {
      navigate("/dealers");
    } else {
      navigate(`/dealers/${selectedState}`);
    }
  };

  const isLoggedIn =
    sessionStorage.getItem("username") !== null;

  return (
    <div>
      <Header />

      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Dealer Name</th>
            <th>City</th>
            <th>Address</th>
            <th>Zip</th>

            <th>
              <select
                name="state"
                id="state"
                value={state || ""}
                onChange={(e) => filterDealers(e.target.value)}
              >
                <option value="" disabled>
                  State
                </option>

                <option value="All">
                  All States
                </option>

                {states.map((stateName) => (
                  <option
                    key={stateName}
                    value={stateName}
                  >
                    {stateName}
                  </option>
                ))}
              </select>
            </th>

            {isLoggedIn && <th>Review Dealer</th>}
          </tr>
        </thead>

        <tbody>
          {dealersList.map((dealer) => (
            <tr key={dealer.id}>
              <td>{dealer.id}</td>

              <td>
                <a href={`/dealer/${dealer.id}`}>
                  {dealer.full_name}
                </a>
              </td>

              <td>{dealer.city}</td>
              <td>{dealer.address}</td>
              <td>{dealer.zip}</td>
              <td>{dealer.state}</td>

              {isLoggedIn && (
                <td>
                  <a href={`/postreview/${dealer.id}`}>
                    <img
                      src={review_icon}
                      className="review_icon"
                      alt="Post Review"
                    />
                  </a>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Dealers;