🐛 Fix chat model tests and improve error handling

## Fixed Issues
- ✅ All 6 failing chat model tests now pass (12/12 tests passing)
- ✅ Fixed DNS resolution errors by properly mocking HTTP client
- ✅ Corrected exception type mismatches in tests
- ✅ Improved error handling in IOIntelligenceChatModel

## Test Improvements
- Use PropertyMock for proper http_client property mocking
- Mock all network calls to avoid connection errors
- Match actual exception types (IOIntelligenceConnectionError)
- Add comprehensive test coverage for all error scenarios

## Code Improvements
- Enhanced exception handling in chat model
- Better null checks for http_client property
- Improved fallback request handling
- More robust error propagation

## Files Changed
- `tests/test_chat.py` - Fixed all failing tests with proper mocking
- `langchain_iointelligence/chat.py` - Improved error handling and property checks
- `.gitignore` - Added temporary development files to ignore list

## Test Results
```
12 passed in 0.36s ✅
```

All chat model functionality is now fully tested and working correctly.
