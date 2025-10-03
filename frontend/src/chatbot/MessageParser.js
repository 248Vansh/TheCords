class MessageParser {
  constructor(actionProvider) {
    this.actionProvider = actionProvider;
  }

  parse(message) {
    const lower = message.toLowerCase();
    this.actionProvider.handleMessage(lower);
  }
}

export default MessageParser;