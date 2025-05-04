import { handleAddModelSubmit } from '../../../ui/mishikallm-dashboard/src/components/add_model/handle_add_model_submit';
import { modelCreateCall } from '../../../ui/mishikallm-dashboard/src/components/networking';

// Mock the dependencies
const mockModelCreateCall = jest.fn().mockResolvedValue({ data: 'success' });
jest.mock('../../../ui/mishikallm-dashboard/src/components/networking', () => ({
  modelCreateCall: async (accessToken: string, formValues: any) => mockModelCreateCall(formValues)
}));

// Also need to mock provider_map
jest.mock('../../../ui/mishikallm-dashboard/src/components/provider_info_helpers', () => ({
  provider_map: {
    'openai': 'openai'
  }
}));

jest.mock('antd', () => ({
  message: {
    error: jest.fn()
  }
}));

describe('handleAddModelSubmit', () => {
  const mockForm = {
    resetFields: jest.fn()
  };
  const mockAccessToken = 'test-token';

  beforeEach(() => {
    jest.clearAllMocks();
    mockModelCreateCall.mockClear();
  });

  it('should not modify model name when all-wildcard is not selected', async () => {
    const formValues = {
      model: 'gpt-4',
      custom_llm_provider: 'openai',
      model_name: 'my-gpt4-deployment'
    };

    await handleAddModelSubmit(formValues, mockAccessToken, mockForm);
    
    console.log('Expected call:', {
      model_name: 'my-gpt4-deployment',
      mishikallm_params: {
        model: 'gpt-4',
        custom_llm_provider: 'openai'
      },
      model_info: {}
    });
    console.log('Actual calls:', mockModelCreateCall.mock.calls);

    expect(mockModelCreateCall).toHaveBeenCalledWith({
      model_name: 'my-gpt4-deployment',
      mishikallm_params: {
        model: 'gpt-4',
        custom_llm_provider: 'openai'
      },
      model_info: {}
    });
    expect(mockForm.resetFields).toHaveBeenCalled();
  });

  it('should handle all-wildcard model correctly', async () => {
    const formValues = {
      model: 'all-wildcard',
      custom_llm_provider: 'openai',
      model_name: 'my-deployment'
    };

    await handleAddModelSubmit(formValues, mockAccessToken, mockForm);

    expect(mockModelCreateCall).toHaveBeenCalledWith({
      model_name: 'openai/*',
      mishikallm_params: {
        model: 'openai/*',
        custom_llm_provider: 'openai'
      },
      model_info: {}
    });
    expect(mockForm.resetFields).toHaveBeenCalled();
  });
});