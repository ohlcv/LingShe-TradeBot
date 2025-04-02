<template>
  <div class="strategy-view">
    <a-card :bordered="false">
      <template #title>
        <div class="strategy-steps">
          <div class="step-item clickable" @click="goToStep('basic')">
            <check-circle-outlined class="step-icon completed" />
            <span class="step-text">基本设置</span>
          </div>
          <div class="step-divider"></div>
          <div class="step-item active">
            <div class="step-number">2</div>
            <span class="step-text">策略参数</span>
          </div>
          <div class="step-divider"></div>
          <div class="step-item clickable" @click="goToStep('risk')">
            <div class="step-number">3</div>
            <span class="step-text">风控配置</span>
          </div>
          <div class="step-divider"></div>
          <div class="step-item clickable" @click="goToStep('finish')">
            <div class="step-number">4</div>
            <span class="step-text">完成</span>
          </div>
        </div>
      </template>

      <h2 class="page-title">TV策略设置</h2>
      
      <a-form
        :model="tvForm"
        layout="vertical"
        class="tv-form"
      >
        <a-card class="settings-card" title="TradingView Webhook配置">
          <a-alert
            type="info"
            show-icon
            banner
            style="margin-bottom: 16px"
            message="TradingView策略说明"
            description="通过TradingView的Webhook功能，您可以将交易信号自动发送到我们的系统进行执行。当您在TradingView上设置的警报触发时，系统将根据收到的信号执行交易操作。"
          />
          
          <a-row :gutter="24">
            <a-col :span="24">
              <a-form-item label="Webhook接收地址">
                <a-input-group compact>
                  <a-input
                    v-model:value="tvForm.webhookUrl"
                    disabled
                    style="width: calc(100% - 50px);"
                  />
                  <a-button
                    type="primary"
                    @click="copyWebhookUrl"
                    style="width: 50px;"
                  >
                    <template #icon><copy-outlined /></template>
                  </a-button>
                </a-input-group>
                <div class="form-item-help">在TradingView中创建警报时，将此URL设置为Webhook地址。每个策略都有唯一的URL，
                  包含用户ID、交易所、交易对和策略ID信息</div>
              </a-form-item>
            </a-col>
          </a-row>

          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="安全密钥">
                <a-input-group compact>
                  <a-input
                    v-model:value="tvForm.apiKey"
                    :disabled="!tvForm.editingKey"
                    style="width: calc(100% - 80px);"
                  />
                  <a-button
                    type="primary"
                    @click="regenerateApiKey"
                    style="width: 30px;"
                    :disabled="!tvForm.editingKey"
                  >
                    <template #icon><reload-outlined /></template>
                  </a-button>
                  <a-button
                    type="link"
                    @click="toggleEditKey"
                    style="width: 50px;"
                  >
                    {{ tvForm.editingKey ? '保存' : '编辑' }}
                  </a-button>
                </a-input-group>
                <div class="form-item-help">用于验证请求来源，必须包含在TradingView警报消息中</div>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="信号有效期">
                <a-input-number
                  v-model:value="tvForm.signalExpiration"
                  :min="1"
                  :max="60"
                  style="width: 100%"
                  addon-after="分钟"
                />
                <div class="form-item-help">超过此时间的信号将被忽略，避免延迟执行过期信号</div>
              </a-form-item>
            </a-col>
          </a-row>
        </a-card>

        <a-card class="settings-card" title="信号处理配置" style="margin-top: 16px">
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="交易数量类型">
                <a-select v-model:value="tvForm.positionSizeType">
                  <a-select-option value="fixed">固定数量</a-select-option>
                  <a-select-option value="percent">账户百分比</a-select-option>
                  <a-select-option value="risk">风险百分比</a-select-option>
                </a-select>
                <div class="form-item-help">决定每次交易的数量计算方式</div>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="交易数量值">
                <a-input-number
                  v-model:value="tvForm.positionSizeValue"
                  :min="0.01"
                  :max="tvForm.positionSizeType === 'fixed' ? 9999 : 100"
                  :step="tvForm.positionSizeType === 'fixed' ? 1 : 0.1"
                  style="width: 100%"
                  :addon-after="positionSizeUnit"
                />
                <div class="form-item-help">
                  {{ positionSizeHelp }}
                </div>
              </a-form-item>
            </a-col>
          </a-row>

          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="允许的信号类型">
                <a-select 
                  v-model:value="tvForm.allowedSignals" 
                  mode="multiple" 
                  placeholder="请选择允许的信号类型"
                >
                  <a-select-option value="buy">买入信号</a-select-option>
                  <a-select-option value="sell">卖出信号</a-select-option>
                  <a-select-option value="close">平仓信号</a-select-option>
                </a-select>
                <div class="form-item-help">设置系统可以接受并处理的信号类型</div>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="信号模式">
                <a-radio-group v-model:value="tvForm.signalMode">
                  <a-radio value="auto">自动执行</a-radio>
                  <a-radio value="manual">人工确认</a-radio>
                </a-radio-group>
                <div class="form-item-help">自动模式下信号将立即执行，人工确认模式需手动确认后执行</div>
                <a-collapse ghost v-if="tvForm.signalMode === 'manual'" style="margin-top: 8px;">
                  <a-collapse-panel key="1" header="查看人工确认模式流程">
                    <div class="confirmation-flow">
                      <ol>
                        <li>TradingView触发警报并发送信号到系统</li>
                        <li>系统将信号保存到待处理队列</li>
                        <li>您会收到站内消息、邮件或App推送通知</li>
                        <li>登录平台查看待处理信号详情</li>
                        <li>您可以选择"确认执行"或"忽略"该信号</li>
                        <li>确认后系统才会执行相应的交易操作</li>
                      </ol>
                      <div class="confirmation-tip">
                        <info-circle-outlined style="color: #1890ff; margin-right: 8px;" />
                        人工确认模式适合需要额外判断或不希望完全自动化的场景，但可能错过某些快速变动的交易机会
                      </div>
                    </div>
                  </a-collapse-panel>
                </a-collapse>
              </a-form-item>
            </a-col>
          </a-row>

          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="订单类型">
                <a-select v-model:value="tvForm.orderType">
                  <a-select-option value="market">市价单</a-select-option>
                  <a-select-option value="limit">限价单</a-select-option>
                </a-select>
                <div class="form-item-help">选择接收信号后下单的订单类型</div>
              </a-form-item>
            </a-col>
            <a-col :span="12" v-if="tvForm.orderType === 'limit'">
              <a-form-item label="限价偏移百分比">
                <a-input-number
                  v-model:value="tvForm.limitPriceOffset"
                  :min="0"
                  :max="5"
                  :step="0.1"
                  style="width: 100%"
                  addon-after="%"
                />
                <div class="form-item-help">相对于信号价格的偏移比例，用于计算限价单价格</div>
              </a-form-item>
            </a-col>
          </a-row>
        </a-card>

        <a-card class="settings-card" title="消息模板配置" style="margin-top: 16px">
          <a-alert
            type="warning"
            show-icon
            style="margin-bottom: 16px"
            message="重要提示"
            description="请确保TradingView警报消息中包含正确的API密钥，否则系统将拒绝处理信号。"
          />

          <a-form-item label="TradingView警报消息模板">
            <a-textarea
              v-model:value="tvForm.messageTemplate"
              :rows="6"
              style="font-family: monospace;"
            />
            <div class="form-item-help">
              在TradingView中创建警报时，将此JSON格式的消息模板粘贴到警报消息框中，
              其中的占位符 <span v-pre>{{...}}</span> 会被TradingView自动替换为实际值
            </div>
          </a-form-item>

          <a-collapse ghost>
            <a-collapse-panel key="1" header="查看可用的TradingView占位符">
              <div class="tv-placeholders">
                <div class="placeholder-group">
                  <h4>通用占位符</h4>
                  <div class="placeholder-item"><code v-pre>{{exchange}}</code> - 交易所名称</div>
                  <div class="placeholder-item"><code v-pre>{{ticker}}</code> - 交易品种代码</div>
                  <div class="placeholder-item"><code v-pre>{{time}}</code> - 信号触发时间</div>
                </div>

                <div class="placeholder-group">
                  <h4>价格数据</h4>
                  <div class="placeholder-item"><code v-pre>{{open}}</code> - 开盘价</div>
                  <div class="placeholder-item"><code v-pre>{{high}}</code> - 最高价</div>
                  <div class="placeholder-item"><code v-pre>{{low}}</code> - 最低价</div>
                  <div class="placeholder-item"><code v-pre>{{close}}</code> - 收盘价</div>
                  <div class="placeholder-item"><code v-pre>{{volume}}</code> - 成交量</div>
                </div>

                <div class="placeholder-group">
                  <h4>策略相关</h4>
                  <div class="placeholder-item"><code v-pre>{{strategy.order.action}}</code> - 买入/卖出动作</div>
                  <div class="placeholder-item"><code v-pre>{{strategy.market_position}}</code> - 市场位置(long/flat/short)</div>
                  <div class="placeholder-item"><code v-pre>{{strategy.position_size}}</code> - 仓位大小</div>
                  <div class="placeholder-item"><code v-pre>{{strategy.order.price}}</code> - 订单价格</div>
                </div>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="2" header="TradingView配置指南">
              <div class="tv-guide">
                <h4>在TradingView中设置警报的步骤</h4>
                <ol>
                  <li>在TradingView中打开<b>{{ baseCurrency }}/{{ quoteCurrency }}</b>交易对的图表</li>
                  <li>添加您的策略或指标到此图表</li>
                  <li>点击右上角"创建警报"按钮</li>
                  <li>在"Webhook URL"字段中粘贴: <br/><code>{{ tvForm.webhookUrl }}</code></li>
                  <li>在"消息"框中粘贴上方提供的消息模板</li>
                  <li>替换模板中的<code>YOUR_API_KEY</code>为: <code>{{ tvForm.apiKey }}</code></li>
                  <li>设置触发条件和其他选项</li>
                  <li>点击"创建"按钮保存警报</li>
                </ol>
                
                <div class="webhook-url-structure">
                  <h4>Webhook URL结构说明</h4>
                  <p>URL格式: <code>https://api.lingshetrading.com/webhook/tv/用户ID/交易所/交易对/策略ID</code></p>
                  <ul>
                    <li><b>用户ID</b>: 您的账户唯一标识</li>
                    <li><b>交易所</b>: 您选择的交易所（如binance）</li>
                    <li><b>交易对</b>: 您选择的交易币对（如BTCUSDT）</li>
                    <li><b>策略ID</b>: 此策略的唯一标识（4位字母数字组合）</li>
                  </ul>
                  <p>系统通过这些参数准确识别信号应由哪个账户的哪个策略处理。</p>
                </div>
                
                <div class="guide-note">
                  <warning-outlined style="color: #faad14; margin-right: 8px;" />
                  <span>
                    请确保您在TradingView中使用的是<b>{{ baseCurrency }}/{{ quoteCurrency }}</b>交易对，
                    与此策略配置的交易对一致，否则收到的信号将不匹配。
                  </span>
                </div>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="3" header="查看实际警报触发消息示例">
              <div class="message-example">
                <h4>当TradingView触发买入信号时:</h4>
                <pre class="example-json">{
  "action": "buy",
  "price": "50123.45",
  "ticker": "BTCUSDT",
  "time": "2023-04-15T14:30:00Z",
  "position": "long",
  "key": "{{ tvForm.apiKey }}"
}</pre>
                
                <h4>当TradingView触发卖出信号时:</h4>
                <pre class="example-json">{
  "action": "sell",
  "price": "51234.56",
  "ticker": "BTCUSDT",
  "time": "2023-04-16T09:45:00Z",
  "position": "flat",
  "key": "{{ tvForm.apiKey }}"
}</pre>

                <h4>当TradingView触发平仓信号时:</h4>
                <pre class="example-json">{
  "action": "close",
  "price": "50789.12",
  "ticker": "BTCUSDT",
  "time": "2023-04-17T16:20:00Z",
  "position": "flat",
  "key": "{{ tvForm.apiKey }}"
}</pre>

                <div class="example-tip">
                  <info-circle-outlined style="color: #1890ff; margin-right: 8px;" />
                  实际接收到的消息可能会因TradingView策略或指标的编写方式而有所不同。
                  系统会尝试从接收到的消息中提取必要的交易信息。
                </div>
              </div>
            </a-collapse-panel>
          </a-collapse>
        </a-card>

        <div class="form-actions">
          <a-space>
            <a-button @click="goBack">
              上一步
            </a-button>
            <a-button type="primary" @click="nextStep">
              下一步
            </a-button>
          </a-space>
        </div>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { message } from 'ant-design-vue';
import { 
  CopyOutlined, 
  ReloadOutlined, 
  CheckCircleOutlined,
  InfoCircleOutlined,
  WarningOutlined
} from '@ant-design/icons-vue';

const router = useRouter();
const route = useRoute();

// 从URL获取基础参数
const exchange = route.query.exchange || 'binance';
const baseCurrency = route.query.baseCurrency || 'BTC';
const quoteCurrency = route.query.quoteCurrency || 'USDT';
const strategyName = route.query.strategyName || 'TV策略';
const symbol = `${baseCurrency}${quoteCurrency}`;
// 接收从CreateStrategy.vue传递的策略ID
const strategyId = route.query.strategyId || generateStrategyId();

// 假设用户ID，实际项目中应从全局状态或API获取
const userId = localStorage.getItem('userId') || 'user1';

// 生成策略ID（使用4字符的短ID）
const generateStrategyId = () => {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = '';
  for (let i = 0; i < 4; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return result;
};

// 生成随机API密钥
const generateApiKey = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < 24; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

// 默认消息模板
const defaultMessageTemplate = JSON.stringify({
  action: "{{strategy.order.action}}",
  price: "{{close}}",
  ticker: "{{ticker}}",
  time: "{{time}}",
  position: "{{strategy.market_position}}",
  key: "YOUR_API_KEY"
}, null, 2);

// 表单数据
const tvForm = reactive({
  name: strategyName,
  webhookUrl: `https://api.lingshetrading.com/webhook/tv/${userId}/${exchange}/${symbol}/${strategyId}`,
  apiKey: generateApiKey(),
  editingKey: false,
  signalExpiration: 5,
  positionSizeType: 'percent',
  positionSizeValue: 10,
  signalMode: 'auto',
  allowedSignals: ['buy', 'sell', 'close'],
  orderType: 'market',
  limitPriceOffset: 0.5,
  messageTemplate: defaultMessageTemplate
});

// 根据选择的交易数量类型返回对应的单位
const positionSizeUnit = computed(() => {
  switch (tvForm.positionSizeType) {
    case 'fixed':
      return '张';
    case 'percent':
    case 'risk':
      return '%';
    default:
      return '';
  }
});

// 交易数量类型帮助文本
const positionSizeHelp = computed(() => {
  switch (tvForm.positionSizeType) {
    case 'fixed':
      return '固定数量模式：每次交易固定张数';
    case 'percent':
      return '账户百分比模式：按账户总额的百分比计算交易数量';
    case 'risk':
      return '风险百分比模式：按每次交易愿意承担的最大亏损比例计算数量';
    default:
      return '';
  }
});

// 复制Webhook URL
const copyWebhookUrl = () => {
  navigator.clipboard.writeText(tvForm.webhookUrl)
    .then(() => {
      message.success('Webhook URL已复制到剪贴板');
    })
    .catch(() => {
      message.error('复制失败，请手动复制');
    });
};

// 生成新的API密钥
const regenerateApiKey = () => {
  tvForm.apiKey = generateApiKey();
  
  // 更新消息模板中的密钥
  tvForm.messageTemplate = tvForm.messageTemplate.replace(
    /"key"\s*:\s*"[^"]*"/,
    `"key": "${tvForm.apiKey}"`
  );
};

// 切换API密钥编辑状态
const toggleEditKey = () => {
  tvForm.editingKey = !tvForm.editingKey;
  
  if (!tvForm.editingKey) {
    // 当保存时，更新消息模板中的密钥
    tvForm.messageTemplate = tvForm.messageTemplate.replace(
      /"key"\s*:\s*"[^"]*"/,
      `"key": "${tvForm.apiKey}"`
    );
  }
};

// 导航到其他步骤
const goToStep = (step) => {
  if (step === 'basic') {
    goBack();
  } else if (step === 'risk') {
    nextStep();
  } else if (step === 'finish') {
    router.push({
      path: '/strategies',
    });
  }
};

// 下一步
const nextStep = () => {
  router.push({
    path: '/strategies/create/risk',
    query: {
      ...route.query,
      strategyType: 'tv',
      isTVStrategy: 'true',
      webhookUrl: tvForm.webhookUrl,
      apiKey: tvForm.apiKey,
      positionSizeType: tvForm.positionSizeType,
      positionSizeValue: tvForm.positionSizeValue.toString(),
      signalMode: tvForm.signalMode,
      tvConfig: JSON.stringify(tvForm)
    }
  });
};

// 返回上一步
const goBack = () => {
  router.push({ 
    path: '/strategies/create', 
    query: {
      ...route.query,
      returnToParams: 'true'
    }
  });
};
</script>

<style scoped>
.strategy-view {
  width: 100%;
  background-color: #f0f2f5;
  padding: 0;
}

.strategy-steps {
  display: flex;
  align-items: center;
  width: 100%;
  margin-bottom: 0;
  padding: 0;
}

.step-item {
  display: flex;
  align-items: center;
  margin-right: 8px;
}

.step-item.clickable {
  cursor: pointer;
}

.step-divider {
  height: 1px;
  background-color: #1890ff;
  flex-grow: 1;
  margin: 0 8px;
}

.step-icon {
  font-size: 18px;
  margin-right: 8px;
  color: #1890ff;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #1890ff;
  color: white;
  font-size: 14px;
  margin-right: 8px;
}

.step-item:not(.active) .step-number {
  background-color: #f0f0f0;
  color: rgba(0, 0, 0, 0.65);
}

.step-text {
  font-size: 14px;
}

.step-item.active .step-text {
  color: #1890ff;
  font-weight: 500;
}

.page-title {
  font-size: 20px;
  font-weight: 500;
  margin: 16px 0 24px 0;
  padding: 0;
}

.tv-form {
  padding: 0 8px;
}

.settings-card {
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 5px rgba(0,0,0,0.05);
}

.form-item-help {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
  margin-top: 4px;
}

.form-actions {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  margin-bottom: 16px;
}

.tv-placeholders {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 24px;
}

.placeholder-group h4 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #1890ff;
  font-size: 14px;
}

.placeholder-item {
  margin-bottom: 8px;
  font-size: 13px;
}

.placeholder-item code {
  background-color: #f5f5f5;
  padding: 2px 5px;
  border-radius: 3px;
  color: #d56161;
}

.tv-guide ol {
  padding-left: 20px;
}

.tv-guide li {
  margin-bottom: 8px;
}

.tv-guide code {
  background-color: #f5f5f5;
  padding: 2px 5px;
  border-radius: 3px;
  color: #1890ff;
  word-break: break-all;
}

.guide-tip {
  background-color: #e6f7ff;
  border-left: 4px solid #1890ff;
  padding: 8px 12px;
  margin-top: 16px;
  border-radius: 0 4px 4px 0;
  display: flex;
  align-items: flex-start;
}

:deep(.ant-collapse-header) {
  color: #1890ff !important;
  padding: 8px 0 !important;
}

:deep(.ant-collapse-content-box) {
  padding: 16px !important;
}

.confirmation-flow {
  padding: 16px;
}

.confirmation-flow ol {
  padding-left: 20px;
}

.confirmation-flow li {
  margin-bottom: 8px;
}

.confirmation-tip {
  background-color: #e6f7ff;
  border-left: 4px solid #1890ff;
  padding: 8px 12px;
  margin-top: 16px;
  border-radius: 0 4px 4px 0;
  display: flex;
  align-items: flex-start;
}

.guide-note {
  background-color: #e6f7ff;
  border-left: 4px solid #faad14;
  padding: 8px 12px;
  margin-top: 16px;
  border-radius: 0 4px 4px 0;
  display: flex;
  align-items: flex-start;
}

.message-example {
  padding: 16px;
}

.example-json {
  background-color: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  margin-bottom: 16px;
}

.example-tip {
  background-color: #e6f7ff;
  border-left: 4px solid #1890ff;
  padding: 8px 12px;
  margin-top: 16px;
  border-radius: 0 4px 4px 0;
  display: flex;
  align-items: flex-start;
}

.webhook-url-structure {
  margin-top: 16px;
  padding: 16px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.webhook-url-structure h4 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #1890ff;
  font-size: 14px;
}

.webhook-url-structure p {
  margin-bottom: 8px;
  font-size: 13px;
}

.webhook-url-structure ul {
  margin-left: 20px;
  margin-bottom: 16px;
}

.webhook-url-structure li {
  margin-bottom: 8px;
}
</style> 