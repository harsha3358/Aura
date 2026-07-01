import { test, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import CaptureSession from "../components/CaptureSession";
import { useAuraStore } from "../store/auraStore";

test("renders CaptureSession root element", () => {
  render(<CaptureSession />);
  const root = screen.getByTestId("capture-session");
  expect(root).toBeInTheDocument();
});

test("renders extraction chips for messages", async () => {
  useAuraStore.setState({
    conversations: [
      {
        id: "conv-123",
        title: "Test Session",
        created_at: new Date().toISOString(),
        messages: [
          {
            id: "msg-abc",
            conversation_id: "conv-123",
            role: "user",
            content: "I decided to use PostgreSQL",
            created_at: new Date().toISOString(),
            facts: [
              {
                id: "fact-1",
                entity: "database",
                value: "PostgreSQL",
                confidence: 0.95,
                review_state: "pending",
                created_at: new Date().toISOString(),
              },
            ],
            decisions: [],
            tasks: [],
            deadlines: [],
          },
        ],
      },
    ],
    activeConversationId: "conv-123",
  });

  render(<CaptureSession />);

  expect(screen.getByText("Test Session")).toBeInTheDocument();
  expect(screen.getByText("I decided to use PostgreSQL")).toBeInTheDocument();
  const chipsContainer = screen.getByTestId("extraction-chips");
  expect(chipsContainer).toBeInTheDocument();
  expect(screen.getByText("database: PostgreSQL")).toBeInTheDocument();
});

test("approve extraction chip triggers store action", async () => {
  const approveMock = vi.fn().mockResolvedValue(true);
  useAuraStore.setState({
    approveKnowledgeItem: approveMock,
    conversations: [
      {
        id: "conv-123",
        title: "Test Session",
        created_at: new Date().toISOString(),
        messages: [
          {
            id: "msg-abc",
            conversation_id: "conv-123",
            role: "user",
            content: "I decided to use PostgreSQL",
            created_at: new Date().toISOString(),
            facts: [
              {
                id: "fact-1",
                entity: "database",
                value: "PostgreSQL",
                confidence: 0.95,
                review_state: "pending",
                created_at: new Date().toISOString(),
              },
            ],
            decisions: [],
            tasks: [],
            deadlines: [],
          },
        ],
      },
    ],
    activeConversationId: "conv-123",
  });

  render(<CaptureSession />);

  const approveButton = screen.getByTestId("approve-button");
  fireEvent.click(approveButton);

  expect(approveMock).toHaveBeenCalledWith({
    type: "fact",
    id: "fact-1",
    messageId: "msg-abc",
  });
});

test("reject extraction chip triggers store action", async () => {
  const rejectMock = vi.fn().mockResolvedValue(true);
  useAuraStore.setState({
    rejectKnowledgeItem: rejectMock,
    conversations: [
      {
        id: "conv-123",
        title: "Test Session",
        created_at: new Date().toISOString(),
        messages: [
          {
            id: "msg-abc",
            conversation_id: "conv-123",
            role: "user",
            content: "I decided to use PostgreSQL",
            created_at: new Date().toISOString(),
            facts: [
              {
                id: "fact-1",
                entity: "database",
                value: "PostgreSQL",
                confidence: 0.95,
                review_state: "pending",
                created_at: new Date().toISOString(),
              },
            ],
            decisions: [],
            tasks: [],
            deadlines: [],
          },
        ],
      },
    ],
    activeConversationId: "conv-123",
  });

  render(<CaptureSession />);

  const rejectButton = screen.getByTestId("reject-button");
  fireEvent.click(rejectButton);

  const rejectPanel = screen.getByTestId("reject-panel");
  expect(rejectPanel).toBeInTheDocument();

  const reasonButton = screen.getByTestId("reject-reason-Wrong Type");
  fireEvent.click(reasonButton);

  expect(rejectMock).toHaveBeenCalledWith({
    type: "fact",
    id: "fact-1",
    reason: "Wrong Type",
    messageId: "msg-abc",
  });
});

test("edit extraction chip triggers store action", async () => {
  const editMock = vi.fn().mockResolvedValue(true);
  useAuraStore.setState({
    updateKnowledgeItem: editMock,
    conversations: [
      {
        id: "conv-123",
        title: "Test Session",
        created_at: new Date().toISOString(),
        messages: [
          {
            id: "msg-abc",
            conversation_id: "conv-123",
            role: "user",
            content: "I decided to use PostgreSQL",
            created_at: new Date().toISOString(),
            facts: [
              {
                id: "fact-1",
                entity: "database",
                value: "PostgreSQL",
                confidence: 0.95,
                review_state: "pending",
                created_at: new Date().toISOString(),
              },
            ],
            decisions: [],
            tasks: [],
            deadlines: [],
          },
        ],
      },
    ],
    activeConversationId: "conv-123",
  });

  render(<CaptureSession />);

  const editButton = screen.getByTestId("edit-button");
  fireEvent.click(editButton);

  const editPanel = screen.getByTestId("edit-panel");
  expect(editPanel).toBeInTheDocument();

  const editInput = screen.getByTestId("edit-input");
  fireEvent.change(editInput, { target: { value: "Postgres v16" } });

  const saveButton = screen.getByTestId("save-button");
  fireEvent.click(saveButton);

  expect(editMock).toHaveBeenCalledWith({
    type: "fact",
    id: "fact-1",
    payload: { value: "Postgres v16" },
    messageId: "msg-abc",
  });
});
