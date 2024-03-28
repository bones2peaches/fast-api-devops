// pages/create-account.tsx
import React from "react";
import CreateAccountForm from "../components/CreateAccountForm";
import Layout from "../components/Layout"; // Make sure to import Layout

const CreateAccountPage: React.FC = () => {
  return (
    <Layout username={null} userId={null} token={null} cookies={null}>
      <div className="py-10">
        <div className="max-w-md mx-auto bg-white shadow-lg rounded-lg p-8">
          <h2 className="mb-6 text-center text-3xl font-bold text-gray-900">
            Create an Account
          </h2>
          <CreateAccountForm />
        </div>
      </div>
    </Layout>
  );
};

export default CreateAccountPage;
