const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors');

const app = express();
const port = 3030;

app.use(cors());
app.use(require('body-parser').urlencoded({ extended: false }));


// ---------------------------------------------------------
// Load JSON data
// ---------------------------------------------------------
const reviews_data = JSON.parse(
  fs.readFileSync("reviews.json", "utf8")
);

const dealerships_data = JSON.parse(
  fs.readFileSync("dealerships.json", "utf8")
);


// ---------------------------------------------------------
// Connect to MongoDB
// ---------------------------------------------------------
mongoose.connect("mongodb://mongo_db:27017/", {
  dbName: "dealershipsDB"
});


// ---------------------------------------------------------
// Import MongoDB models
// ---------------------------------------------------------
const Reviews = require('./review');
const Dealerships = require('./dealership');


// ---------------------------------------------------------
// Populate database
// ---------------------------------------------------------
try {
  Reviews.deleteMany({}).then(() => {
    Reviews.insertMany(reviews_data['reviews']);
  });

  Dealerships.deleteMany({}).then(() => {
    Dealerships.insertMany(dealerships_data['dealerships']);
  });

} catch (error) {
  console.log("Error populating database:", error);
}


// ---------------------------------------------------------
// Home Route
// ---------------------------------------------------------
app.get('/', async (req, res) => {
  res.send("Welcome to the Mongoose API");
});


// ---------------------------------------------------------
// Q8 - Fetch all reviews
// ---------------------------------------------------------
app.get('/fetchReviews', async (req, res) => {
  try {
    const documents = await Reviews.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({
      error: 'Error fetching documents'
    });
  }
});


// ---------------------------------------------------------
// Q8 - Fetch reviews for a particular dealer
// ---------------------------------------------------------
app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    const documents = await Reviews.find({
      dealership: req.params.id
    });

    res.json(documents);

  } catch (error) {
    res.status(500).json({
      error: 'Error fetching documents'
    });
  }
});


// ---------------------------------------------------------
// Q9 - Fetch all dealerships
// ---------------------------------------------------------
app.get('/fetchDealers', async (req, res) => {
  try {
    const documents = await Dealerships.find();

    res.json(documents);

  } catch (error) {
    res.status(500).json({
      error: 'Error fetching dealerships'
    });
  }
});


// ---------------------------------------------------------
// Q11 - Fetch dealerships by state
// Example: /fetchDealers/KS
// ---------------------------------------------------------
app.get('/fetchDealers/:state', async (req, res) => {
  try {
    const documents = await Dealerships.find({
      state: req.params.state
    });

    res.json(documents);

  } catch (error) {
    res.status(500).json({
      error: 'Error fetching dealerships'
    });
  }
});


// ---------------------------------------------------------
// Q10 - Fetch dealership by ID
// Example: /fetchDealer/1
// ---------------------------------------------------------
app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const documents = await Dealerships.find({
      id: req.params.id
    });

    res.json(documents);

  } catch (error) {
    res.status(500).json({
      error: 'Error fetching dealership'
    });
  }
});


/// ---------------------------------------------------
// Insert a new review
// ---------------------------------------------------
app.post(
  '/insert_review',
  express.json(),
  async (req, res) => {
    try {
      const data = req.body;

      const documents = await Reviews
        .find()
        .sort({ id: -1 });

      let new_id = 1;

      if (documents.length > 0) {
        new_id = documents[0].id + 1;
      }

      const review = new Reviews({
        id: new_id,
        name: data.name,
        dealership: Number(data.dealership),
        review: data.review,
        purchase: data.purchase,
        purchase_date: data.purchase_date,
        car_make: data.car_make,
        car_model: data.car_model,
        car_year: Number(data.car_year),
        sentiment: data.sentiment
      });

      const savedReview = await review.save();

      res.status(200).json(savedReview);

    } catch (error) {
      console.log(error);

      res.status(500).json({
        error: 'Error inserting review'
      });
    }
  }
);

// ---------------------------------------------------------
// Start Express Server
// ---------------------------------------------------------
app.listen(port, () => {
  console.log(
    `Server is running on http://localhost:${port}`
  );
});