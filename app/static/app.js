const chatForm=document.getElementById("chatForm");
const messageInput=document.getElementById("messageInput");
const chatMessages=document.getElementById("chatMessages");
const sendButton=document.getElementById("sendButton");
const newConversationButton=document.getElementById("newConversationButton");
const statusText=document.getElementById("statusText");

console.log("app.js loaded");
console.log("Element refs:", {
    chatForm, messageInput, chatMessages, sendButton, newConversationButton, statusText
});

if (!chatForm) console.error("Missing element: #chatForm");
if (!messageInput) console.error("Missing element: #messageInput");
if (!chatMessages) console.error("Missing element: #chatMessages");
if (!sendButton) console.error("Missing element: #sendButton");
if (!newConversationButton) console.error("Missing element: #newConversationButton");
if (!statusText) console.error("Missing element: #statusText");

let conversationId=null;

function addMessage(role,text) {
    const wrapper = document.createElement("div");
    wrapper.classList.add(
        "message",
        role === "user" ? "user-message":"assistant-message"
    );
    const bubble=document.createElement("div");
    bubble.classList.add("bubble");
    bubble.textContent=text;
    wrapper.appendChild(bubble);
    chatMessages.appendChild(wrapper);
    chatMessages.scrollTop=chatMessages.scrollHeight;
    return bubble;
}

chatForm.addEventListener(
    "submit",
    async function(event) {
        event.preventDefault();

        console.log("chatForm submit event fired");

        const message=messageInput.value.trim();

        console.log("Submitting message:", message);

        if(!message) {
            return;
        }

        addMessage("user",message);

        const assistantBubble= addMessage("assistant","");
        messageInput.value="";
        sendButton.disabled=true;
        statusText.textContent="Generating Response...";

        try{
            console.log("Calling streamChatResponse", { message, conversationId });
            await streamChatResponse(
                message, assistantBubble
            );
            console.log("streamChatResponse resolved");
        }
        catch(error) {
            console.error(error);
            assistantBubble.textContent="Something went wrong.";
            statusText.textContent="Request Failed.";
        }
        finally {
            sendButton.disabled=false;
            messageInput.focus();
        }
    }
)

async function streamChatResponse(
    message, assistantBubble
) {
    console.log("streamChatResponse start", { message, conversationId });
    const response = await fetch("/chat/stream",{
        method: "POST",
        headers: {"Content-type": "application/json"},
        body: JSON.stringify({
            message: message, 
            conversationId: conversationId
        })
    });

    console.log("fetch returned", response.status, response.ok);

    if(!response.ok)
    {
        throw new Error(
           `HTTP error:${response.status}`
        );
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer="";
    while(true){
        const{value, done}=await reader.read();
    
        if(done) {
            break;
        }

        buffer += decoder.decode(
            value,
            {stream: true}
        );

        const events = buffer.split("\n\n");

        buffer = events.pop() || "";
        for(const eventText of events) {
            console.log("SSE chunk:", eventText);
            handleSseEvent(
                eventText, assistantBubble
            );
        }
    }
    statusText.textContent="Response Complete.";
    console.log("streamChatResponse complete");
}

function handleSseEvent(
    eventText, assistantBubble
) {
    const lines= eventText.split("\n");

    let eventName = null;

    let dataText="";

    for(const line of lines) {
        if(line.startsWith("event:"))
        {
            eventName=line.substring(6).trim();
        }
        if(line.startsWith("data:"))
        {
            dataText+=line.substring(5).trim();
        }
    }

    console.log("handleSseEvent parsed:", { eventName, dataText });

    if(!eventName || !dataText)
    {
        return;
    }

    const data = JSON.parse(dataText);

    if(eventName==="conversation")
    {
        conversationId=data.conversation_id;
        console.log("Conversation:",conversationId);
    }
    else if (eventName==="text")
    {
        assistantBubble.textContent += data.delta;
        chatMessages.scrollTop=chatMessages.scrollHeight;
    }
    else if (eventName==="completed")
    {
        statusText.textContent="Response Complete.";
    }
    else if(eventName==="error")
    {
        assistantBubble.textContent += "\n\nError: " + data.message;
        statusText.textContent="Streaming error.";
    }
}

newConversationButton.addEventListener(
    "click", async function() {

        if(conversationId) {
            try{
                await fetch(
                    `/chat/${conversationId}`,
                    {
                        method: "DELETE"
                    }
                );
            }
            catch(error){
                console.error(
                    "Could not delete conversation",
                    error
                );
            }
        }
        conversationId=null;
        chatMessages.innerHTML="";
        statusText.textContent="Started a new Conversation.";
        messageInput.focus();
    }
);

