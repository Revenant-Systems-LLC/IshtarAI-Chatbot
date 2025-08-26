using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UIElements;

public class GameManager : MonoBehaviour
{
    [Header("UI Elements")]
    [SerializeField]
    private UIDocument chatUIDocument;

    private TextField userInputField;
    private ScrollView chatDisplayArea;
    private Button sendButton;

    [Header("Backend Configuration")]
    [SerializeField]
    private string backendUrl = "http://127.0.0.1:5000/chat";
    [SerializeField]
    private string currentPersonaId = "arayah";

    // --- SESSION & STATE MANAGEMENT ---
    private string currentSessionId;
    private string currentEmotionalState = "Neutral";
    private int currentRelationshipScore = 0;

    void OnEnable()
    {
        VisualElement root = chatUIDocument.rootVisualElement;

        userInputField = root.Q<TextField>("UserInputField");
        chatDisplayArea = root.Q<ScrollView>("ChatDisplayArea");
        sendButton = root.Q<Button>("SendButton");

        if (sendButton != null)
        {
            sendButton.clicked += OnSendButtonClicked;
        }
        if (userInputField != null)
        {
            userInputField.RegisterCallback<KeyDownEvent>(OnInputKeyDown);
        }

        StartNewSession();
    }

    void OnDisable()
    {
        if (sendButton != null)
        {
            sendButton.clicked -= OnSendButtonClicked;
        }
        if (userInputField != null)
        {
            userInputField.UnregisterCallback<KeyDownEvent>(OnInputKeyDown);
        }
    }

    public void StartNewSession(string personaId = "arayah")
    {
        currentSessionId = System.Guid.NewGuid().ToString();
        currentPersonaId = personaId;
        currentEmotionalState = "Neutral";
        currentRelationshipScore = 0;

        chatDisplayArea.Clear();
        AppendMessage($"New session started with {currentPersonaId}.", "System");
        UnityEngine.Debug.Log($"New session started with {currentPersonaId}. Session ID: {currentSessionId}");
    }

    private void OnInputKeyDown(KeyDownEvent evt)
    {
        if (evt.keyCode == KeyCode.Return || evt.keyCode == KeyCode.KeypadEnter)
        {
            OnSendButtonClicked();
        }
    }

    private void OnSendButtonClicked()
    {
        string userInput = userInputField.value;
        if (string.IsNullOrWhiteSpace(userInput))
        {
            return;
        }

        AppendMessage(userInput, "User");
        userInputField.value = string.Empty;
        StartCoroutine(SendChatRequest(userInput));
    }

    private IEnumerator SendChatRequest(string message)
    {
        ChatRequestData requestData = new ChatRequestData
        {
            user_input = message,
            persona_id = currentPersonaId,
            session_id = currentSessionId
        };

        string jsonPayload = JsonUtility.ToJson(requestData);
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonPayload);

        UnityWebRequest request = new UnityWebRequest(backendUrl, "POST");
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            UnityEngine.Debug.LogError($"Error sending request: {request.error}");
            AppendMessage($"System Error: Could not connect to AI. ({request.error})", "System");
        }
        else
        {
            string jsonResponse = request.downloadHandler.text;
            UnityEngine.Debug.Log($"Received raw response: {jsonResponse}");
            ChatResponseData responseData = JsonUtility.FromJson<ChatResponseData>(jsonResponse);

            currentEmotionalState = responseData.new_state;
            currentRelationshipScore = responseData.relationship_score;

            AppendMessage(responseData.response_text, responseData.persona_display_name);

            UnityEngine.Debug.Log($"State Updated -> Emotional State: {currentEmotionalState}, Relationship Score: {currentRelationshipScore}");
        }
    }

    private void AppendMessage(string message, string sender)
    {
        // Explicitly declare the type to resolve ambiguity
        UnityEngine.UIElements.Label newLabel = new UnityEngine.UIElements.Label();
        newLabel.text = $"<color=yellow>{sender}:</color> {message}";
        newLabel.style.whiteSpace = WhiteSpace.Normal;

        if (chatDisplayArea != null)
        {
            chatDisplayArea.Add(newLabel);
            chatDisplayArea.schedule.Execute(() => chatDisplayArea.ScrollTo(newLabel)).StartingIn(10);
        }
    }

    // --- Updated Data Structures for V2 API ---
    [System.Serializable]
    public class ChatRequestData
    {
        public string user_input;
        public string persona_id;
        public string session_id;
    }

    [System.Serializable]
    public class ChatResponseData
    {
        public string response_text;
        public string persona_id;
        public string persona_display_name;
        public string new_state;
        public int relationship_score;
    }
}