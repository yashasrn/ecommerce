import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Signup from "./pages/Signup";
import Login from "./pages/loginpage";
import ProductsPage from "./pages/ProductsPage";
import CartPage from "./pages/CartPageTemp";
import BuyNowPage from "./pages/BuyNowPage";
import CheckoutPage from "./pages/CheckoutPage";
import MyOrdersPage from "./pages/MyOrdersPage";
import PaymentPage from "./pages/PaymentPage";
import Logout from "./components/LogoutPage";
import OrderConfirmationPage from "./pages/OrderConfirmationPage";
import AddProduct from "./pages/AddProduct";
import SellerLogin from "./pages/SellerLogin";
import ProductsList from "./pages/ProductList";
import ProtectedSellerRoute from "./components/ProtectedSellerRoute";
import SellerSignup from "./pages/SellerSignup";
import SellerDashboard from "./components/SellerDashboard";
import EditProduct from "./components/EditProduct";
import ContactUs from "./pages/ContactUs";
import ForgotPassword from "./pages/ForgotPassword";

function App() {
  return (
    <Router>
      <Routes>
        {/* ================================ */}
        {/*  DEFAULT ROUTE */}
        {/* ================================ */}
        <Route path="/" element={<Navigate to="/login" replace />} />

        {/* ================================ */}
        {/*  USER ROUTES (Customers) */}
        {/* ================================ */}
        <Route path="/signup" element={<Signup />} />
        <Route path="/my-orders" element={<MyOrdersPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/buy/:id" element={<BuyNowPage />} />
        <Route path="/checkout" element={<CheckoutPage />} />
        <Route path="/payment" element={<PaymentPage />} />
        <Route path="/confirmation" element={<OrderConfirmationPage />} />
        <Route path="/contactus" element={<ContactUs />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
<Route path="/seller-forgot-password" element={<ForgotPassword />} />


        {/* ================================ */}
        {/*  SELLER PUBLIC ROUTES (No Login Required) */}
        {/* ================================ */}
        <Route path="/seller-signup" element={<SellerSignup />} />
        <Route path="/seller-login" element={<SellerLogin />} />


        {/* ================================ */}
        {/*  SELLER PROTECTED ROUTES (Approved Sellers Only) */}
        {/* ================================ */}
        <Route
          path="/seller-dashboard"
          element={
            <ProtectedSellerRoute>
              <SellerDashboard />
            </ProtectedSellerRoute>
          }
        />
        <Route
          path="/add-product"
          element={
            <ProtectedSellerRoute>
              <AddProduct />
            </ProtectedSellerRoute>
          }
        />
        <Route
          path="/edit-product/:id"
          element={
            <ProtectedSellerRoute>
              <EditProduct />
            </ProtectedSellerRoute>
          }
        />

        {/* ================================ */}
        {/*  PRODUCT LIST (Public or Admin?) */}
        {/* ================================ */}
        <Route path="/product" element={<ProductsList />} />
      </Routes>

      {/* Chatbot removed */}
    </Router>
  );
}

export default App;