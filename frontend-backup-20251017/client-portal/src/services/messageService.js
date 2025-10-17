import axiosInstance from "../utils/axiosInstance";

export const sendMessage = async (receiverId, content) => {
  const response = await axiosInstance.post("/messages/", {
    receiver_id: receiverId,
    content,
  });
  return response.data;
};

export const getConversation = async (userId) => {
  const response = await axiosInstance.get(`/messages/conversation/${userId}`);
  return response.data;
};
