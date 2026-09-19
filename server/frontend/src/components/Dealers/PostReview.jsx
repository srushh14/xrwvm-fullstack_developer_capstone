import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import "./Dealers.css";
import "../assets/style.css";
import Header from "../Header/Header";

const PostReview = () => {
  const [dealer, setDealer] = useState({});
  const [review, setReview] = useState("");
  const [model, setModel] = useState("");
  const [year, setYear] = useState("");
  const [date, setDate] = useState("");
  const [carmodels, setCarmodels] = useState([]);

  const params = useParams();
  const id = params.id;

  const dealer_url = `/djangoapp/dealer/${id}`;
  const review_url = `/djangoapp/add_review`;
  const carmodels_url = `/djangoapp/get_cars`;

  // ---------------------------------------------------
  // POST REVIEW
  // ---------------------------------------------------

  const postreview = async () => {
    const firstName = sessionStorage.getItem("firstname");
    const lastName = sessionStorage.getItem("lastname");
    const username = sessionStorage.getItem("username");

    // Use first + last name if available.
    // Otherwise use the logged-in username.
    // Fallback prevents MongoDB "name is required" error.
    let name = "";

    if (firstName && lastName) {
      name = `${firstName} ${lastName}`;
    } else if (username) {
      name = username;
    } else {
      name = "root";
    }

    // Validate all fields
    if (
      !model ||
      review.trim() === "" ||
      date === "" ||
      year === ""
    ) {
      alert("All details are mandatory");
      return;
    }

    const model_split = model.split("|");

    const make_chosen = model_split[0];
    const model_chosen = model_split[1];

    const jsoninput = JSON.stringify({
      name: name,
      dealership: id,
      review: review,
      purchase: true,
      purchase_date: date,
      car_make: make_chosen,
      car_model: model_chosen,
      car_year: year,
    });

    try {
      const res = await fetch(review_url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: jsoninput,
      });

      const json = await res.json();

      console.log("Review response:", json);

      if (json.status === 200) {
        window.location.href = `/dealer/${id}`;
      } else {
        alert("Review could not be submitted.");
      }
    } catch (error) {
      console.error("Error submitting review:", error);
      alert("Error submitting review.");
    }
  };

  // ---------------------------------------------------
  // GET DEALER DETAILS
  // ---------------------------------------------------

  const get_dealer = async () => {
    try {
      const res = await fetch(dealer_url);

      const retobj = await res.json();

      if (retobj.status === 200) {
        const dealerobjs = Array.from(retobj.dealer);

        if (dealerobjs.length > 0) {
          setDealer(dealerobjs[0]);
        }
      }
    } catch (error) {
      console.error(
        "Error getting dealer:",
        error
      );
    }
  };

  // ---------------------------------------------------
  // GET CAR MAKES AND MODELS
  // ---------------------------------------------------

  const get_cars = async () => {
    try {
      const res = await fetch(carmodels_url);

      const retobj = await res.json();

      if (retobj.CarModels) {
        setCarmodels(
          Array.from(retobj.CarModels)
        );
      }
    } catch (error) {
      console.error(
        "Error getting car models:",
        error
      );
    }
  };

  // ---------------------------------------------------
  // LOAD PAGE DATA
  // ---------------------------------------------------

  useEffect(() => {
    get_dealer();
    get_cars();
  }, []);

  // ---------------------------------------------------
  // PAGE
  // ---------------------------------------------------

  return (
    <div>
      <Header />

      <div style={{ margin: "5%" }}>

        <h1 style={{ color: "darkblue" }}>
          Post Review for {dealer.full_name}
        </h1>

        <div className="input_field">

          <label>Review</label>

          <br />

          <textarea
            id="review"
            cols="50"
            rows="7"
            value={review}
            placeholder="Enter your review"
            onChange={(e) =>
              setReview(e.target.value)
            }
          />

        </div>

        <div className="input_field">

          Purchase Date{" "}

          <input
            type="date"
            value={date}
            onChange={(e) =>
              setDate(e.target.value)
            }
          />

        </div>

        <div className="input_field">

          Car Make and Model{" "}

          <select
            name="cars"
            id="cars"
            value={model}
            onChange={(e) =>
              setModel(e.target.value)
            }
          >

            <option value="" disabled>
              Choose Car Make and Model
            </option>

            {carmodels.map((carmodel) => (

              <option
                key={carmodel.id}
                value={`${carmodel.car_make}|${carmodel.name}`}
              >
                {carmodel.car_make}{" "}
                {carmodel.name}
              </option>

            ))}

          </select>

        </div>

        <div className="input_field">

          Car Year{" "}

          <input
            type="number"
            value={year}
            min="2015"
            max="2023"
            onChange={(e) =>
              setYear(e.target.value)
            }
          />

        </div>

        <div>

          <button
            className="postreview"
            onClick={postreview}
          >
            Post Review
          </button>

        </div>

      </div>
    </div>
  );
};

export default PostReview;