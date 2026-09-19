import { Routes, Route } from "react-router-dom";

import Dealers from "./components/Dealers/Dealers";
import Dealer from "./components/Dealers/Dealer";
import PostReview from "./components/Dealers/PostReview";
import LoginPanel from "./components/Login/Login";
import Register from "./components/Register/Register";

function App() {
  return (
    <Routes>

      {/* Dealers Home Page */}
      <Route path="/" element={<Dealers />} />

      {/* All Dealers */}
      <Route path="/dealers" element={<Dealers />} />

      {/* Dealers Filtered by State */}
      <Route path="/dealers/:state" element={<Dealers />} />

      {/* Individual Dealer Details and Reviews */}
      <Route path="/dealer/:id" element={<Dealer />} />

      {/* Login */}
      <Route path="/login" element={<LoginPanel />} />

      {/* Register */}
      <Route path="/register" element={<Register />} />

      {/* Post Dealer Review */}
      <Route path="/postreview/:id" element={<PostReview />} />

    </Routes>
  );
}

export default App;