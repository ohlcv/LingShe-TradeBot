<template>
  <div class="risk-management">
    <!-- 顶部标题 -->
    <div class="page-header-container">
      <a-card :bordered="false" class="header-card">
        <div class="page-header">
          <h1>系统风控管理</h1>
          <div class="emergency-button">
            <a-button type="primary" danger @click="emergencyStopAll">
              紧急停止所有交易
            </a-button>
          </div>
        </div>
      </a-card>
    </div>

    <!-- 系统风控条件 -->
    <a-card title="系统风控条件" :bordered="false" class="risk-card">
      <a-row :gutter="24">
        <a-col :span="8">
          <a-card class="risk-condition-card" title="最大持仓币种数">
            <template #extra>
              <a-tooltip title="设置系统最大同时持仓的币种数量。当达到最大值时，新的交易信号将被忽略，直到有币种平仓。">
                <question-circle-outlined style="cursor: pointer" />
              </a-tooltip>
            </template>
            <a-input-number
              v-model:value="maxPositionCoins"
              style="width: 100%"
              :min="0"
              :max="100"
              placeholder="不限制"
              :formatter="(value: any) => value === 0 ? '∞' : value"
              :parser="(value: string) => value === '∞' ? 0 : Number(value)"
              @change="handleMaxPositionsChange"
            />
            <div class="risk-status">
              <div class="risk-indicator">
                当前持仓: <span class="active-value">{{activePositions}}/{{maxPositionCoins === 0 ? '∞' : maxPositionCoins}}</span>
              </div>
              <template v-if="maxPositionCoins > 0">
                <a-progress 
                  :percent="Math.min(100, (activePositions / maxPositionCoins) * 100)"
                  :stroke-color="activePositions >= maxPositionCoins ? '#ff4d4f' : '#1890ff'"
                  :status="activePositions >= maxPositionCoins ? 'exception' : 'normal'"
                  :show-info="false"
                  size="small"
                  style="margin-top: 8px"
                />
              </template>
            </div>
          </a-card>
        </a-col>
        <a-col :span="8">
          <a-card class="risk-condition-card" title="最大持仓价值">
            <template #extra>
              <a-tooltip title="设置系统最大同时持仓的总价值。当达到最大值时，新的交易信号将被忽略。">
                <question-circle-outlined style="cursor: pointer" />
              </a-tooltip>
            </template>
            <a-input-number
              v-model:value="maxPositionValue"
              style="width: 100%"
              :min="0"
              :step="1000"
              placeholder="不限制"
              :formatter="(value: any) => value === 0 ? '∞' : value"
              :parser="(value: string) => value === '∞' ? 0 : Number(value)"
              addon-after="USDT"
              @change="handleMaxPositionValueChange"
            />
            <div class="risk-status">
              <div class="risk-indicator">
                当前持仓价值: <span class="active-value">{{totalPositionValue.toLocaleString()}} USDT</span>
              </div>
              <template v-if="maxPositionValue > 0">
                <a-progress 
                  :percent="Math.min(100, (totalPositionValue / maxPositionValue) * 100)"
                  :stroke-color="totalPositionValue >= maxPositionValue ? '#ff4d4f' : '#1890ff'"
                  :status="totalPositionValue >= maxPositionValue ? 'exception' : 'normal'"
                  :show-info="false"
                  size="small"
                  style="margin-top: 8px"
                />
              </template>
            </div>
          </a-card>
        </a-col>
        <a-col :span="8">
          <a-card class="risk-condition-card" title="最大亏损停止">
            <template #extra>
              <a-tooltip title="设置系统级最大亏损阈值。当系统亏损达到此值时，将自动暂停所有运行中的策略。">
                <question-circle-outlined style="cursor: pointer" />
              </a-tooltip>
            </template>
            <a-input-number
              v-model:value="maxLossCutoff"
              style="width: 100%"
              :min="0"
              :step="100"
              placeholder="不限制"
              :formatter="(value: any) => value === 0 ? '∞' : value"
              :parser="(value: string) => value === '∞' ? 0 : Number(value)"
              addon-after="USDT"
              @change="handleMaxLossCutoffChange"
            />
            <div class="risk-status">
              <template v-if="maxLossCutoff > 0">
                <div class="risk-indicator">
                  当前亏损: <span class="active-value">{{currentMaxLoss.toLocaleString()}}/{{maxLossCutoff.toLocaleString()}} USDT</span>
                </div>
                <a-progress 
                  :percent="Math.min(100, (currentMaxLoss / maxLossCutoff) * 100)"
                  :stroke-color="currentMaxLoss >= maxLossCutoff ? '#ff4d4f' : '#1890ff'"
                  :status="currentMaxLoss >= maxLossCutoff ? 'exception' : 'normal'"
                  :show-info="false"
                  size="small"
                  style="margin-top: 8px"
                />
              </template>
              <template v-else>
                <div class="risk-indicator">
                  当前亏损: <span class="active-value">{{currentMaxLoss.toLocaleString()}} USDT</span>
                </div>
              </template>
            </div>
          </a-card>
        </a-col>
      </a-row>
    </a-card>

    <!-- 主要风控配置区域 -->
    <div class="risk-config-section">
      <!-- 账户安全风控 -->
      <a-card title="账户安全风控" :bordered="false" class="risk-card">
        <a-form :model="accountRiskForm" layout="vertical">
          <a-row :gutter="24">
            <a-col :span="24">
              <a-form-item label="最大亏损限制" name="lossLimit">
                <div class="input-with-select">
                  <a-input-number 
                    v-model:value="accountRiskForm.lossLimit" 
                    style="width: 60%"
                    :min="0"
                    :step="100"
                    addon-after="USDT"
                  />
                  <a-select 
                    v-model:value="accountRiskForm.timeUnit" 
                    style="width: 40%"
                  >
                    <a-select-option value="hour">每小时</a-select-option>
                    <a-select-option value="day">每日</a-select-option>
                    <a-select-option value="week">每周</a-select-option>
                  </a-select>
                </div>
                <div class="form-item-help">单位时间内亏损达到此金额时，自动暂停相关策略</div>
              </a-form-item>
            </a-col>
          </a-row>
        </a-form>
      </a-card>

      <!-- 市场风险风控 -->
      <a-card title="市场风险风控" :bordered="false" class="risk-card">
        <a-form :model="marketRiskForm" layout="vertical">
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="价格异常波动监控" name="priceVolatilityMonitoring">
                <a-switch v-model:checked="marketRiskForm.priceVolatilityMonitoring" />
                <div class="form-item-help">检测价格异常波动并采取保护措施</div>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="波动阈值" name="volatilityThreshold" v-if="marketRiskForm.priceVolatilityMonitoring">
                <a-input-number 
                  v-model:value="marketRiskForm.volatilityThreshold" 
                  style="width: 100%"
                  :min="0.5"
                  :max="20"
                  :step="0.5"
                  addon-after="%"
                />
                <div class="form-item-help">短时价格波动超过此比例时触发保护</div>
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="24" v-if="marketRiskForm.priceVolatilityMonitoring">
            <a-col :span="12">
              <a-form-item label="监控时间窗口" name="volatilityTimeWindow">
                <div class="input-with-select">
                  <a-input-number 
                    v-model:value="marketRiskForm.volatilityTimeWindow" 
                    style="width: 60%"
                    :min="1"
                    :step="1"
                  />
                  <a-select 
                    v-model:value="marketRiskForm.volatilityTimeUnit" 
                    style="width: 40%"
                  >
                    <a-select-option value="minute">分钟</a-select-option>
                    <a-select-option value="hour">小时</a-select-option>
                    <a-select-option value="day">天</a-select-option>
                  </a-select>
                </div>
                <div class="form-item-help">指定时间窗口内监测价格波动</div>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="波动计算方式" name="volatilityCalculationMethod">
                <a-select 
                  v-model:value="marketRiskForm.volatilityCalculationMethod" 
                  style="width: 100%"
                >
                  <a-select-option value="highLow">最高价-最低价</a-select-option>
                  <a-select-option value="standardDeviation">标准差</a-select-option>
                  <a-select-option value="atr">平均真实波幅(ATR)</a-select-option>
                </a-select>
                <div class="form-item-help">选择波动率的计算方法</div>
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="流动性监控" name="liquidityMonitoring">
                <a-switch v-model:checked="marketRiskForm.liquidityMonitoring" />
                <div class="form-item-help">监控交易对流动性，预防滑点风险</div>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="最大允许滑点" name="maxAllowedSlippage" v-if="marketRiskForm.liquidityMonitoring">
                <a-input-number 
                  v-model:value="marketRiskForm.maxAllowedSlippage" 
                  style="width: 100%"
                  :min="0.1"
                  :max="5"
                  :step="0.1"
                  addon-after="%"
                />
                <div class="form-item-help">超过此滑点的订单将被拒绝执行</div>
              </a-form-item>
            </a-col>
          </a-row>
        </a-form>
      </a-card>

      <!-- 技术风控 -->
      <a-card title="技术风控" :bordered="false" class="risk-card">
        <a-form :model="techRiskForm" layout="vertical">
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="API响应超时监控" name="apiTimeoutMonitoring">
                <a-switch v-model:checked="techRiskForm.apiTimeoutMonitoring" />
                <div class="form-item-help">监控交易所API响应状态</div>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="API超时阈值" name="apiTimeoutThreshold" v-if="techRiskForm.apiTimeoutMonitoring">
                <a-input-number 
                  v-model:value="techRiskForm.apiTimeoutThreshold" 
                  style="width: 100%"
                  :min="100"
                  :max="10000"
                  :step="100"
                  addon-after="毫秒"
                />
                <div class="form-item-help">API响应超过此时间视为超时</div>
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="交易所连接状态监控" name="exchangeConnMonitoring">
                <a-switch v-model:checked="techRiskForm.exchangeConnMonitoring" />
                <div class="form-item-help">监控与交易所的网络连接状态</div>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="自动重连尝试次数" name="autoReconnectAttempts" v-if="techRiskForm.exchangeConnMonitoring">
                <a-input-number 
                  v-model:value="techRiskForm.autoReconnectAttempts" 
                  style="width: 100%"
                  :min="1"
                  :max="10"
                  :step="1"
                />
                <div class="form-item-help">连接断开后自动尝试重连的次数</div>
              </a-form-item>
            </a-col>
          </a-row>
        </a-form>
      </a-card>

      <!-- 时间风控 -->
      <a-card title="时间风控" :bordered="false" class="risk-card">
        <a-form :model="timeRiskForm" layout="vertical">
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="交易时间限制" name="tradingTimeLimit">
                <a-switch v-model:checked="timeRiskForm.tradingTimeLimit" />
                <div class="form-item-help">仅在特定时间段内允许交易</div>
              </a-form-item>
            </a-col>
            <a-col :span="12" v-if="timeRiskForm.tradingTimeLimit">
              <a-form-item label="交易日" name="tradingDays">
                <a-select
                  v-model:value="timeRiskForm.tradingDays"
                  mode="multiple"
                  style="width: 100%"
                  placeholder="选择交易日"
                >
                  <a-select-option value="1">星期一</a-select-option>
                  <a-select-option value="2">星期二</a-select-option>
                  <a-select-option value="3">星期三</a-select-option>
                  <a-select-option value="4">星期四</a-select-option>
                  <a-select-option value="5">星期五</a-select-option>
                  <a-select-option value="6">星期六</a-select-option>
                  <a-select-option value="0">星期日</a-select-option>
                </a-select>
                <div class="form-item-help">选择允许交易的日期</div>
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="24" v-if="timeRiskForm.tradingTimeLimit">
            <a-col :span="12">
              <a-form-item label="交易开始时间" name="tradingStartTime">
                <a-time-picker
                  v-model:value="timeRiskForm.tradingStartTime"
                  format="HH:mm:ss"
                  style="width: 100%"
                />
                <div class="form-item-help">每日交易开始时间</div>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="交易结束时间" name="tradingEndTime">
                <a-time-picker
                  v-model:value="timeRiskForm.tradingEndTime"
                  format="HH:mm:ss"
                  style="width: 100%"
                />
                <div class="form-item-help">每日交易结束时间</div>
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="重要时间点禁止交易" name="timePointLimit">
                <a-switch v-model:checked="timeRiskForm.timePointLimit" />
                <div class="form-item-help">在特定时间点前后停止交易（如重要数据发布时间）</div>
              </a-form-item>
            </a-col>
            <a-col :span="12" v-if="timeRiskForm.timePointLimit">
              <a-form-item label="重要时间点设置" name="forbiddenTimePoints">
                <a-button 
                  type="dashed" 
                  style="width: 100%"
                  @click="showTimePointsModal"
                >
                  <template #icon><PlusOutlined /></template>
                  添加/管理时间点
                </a-button>
                <div class="form-item-help">已设置 {{timeRiskForm.forbiddenTimePoints.length}} 个重要时间点</div>
              </a-form-item>
            </a-col>
          </a-row>
        </a-form>
      </a-card>
    </div>

    <!-- 底部操作区域 -->
    <div class="risk-actions">
      <a-button type="primary" size="large" @click="saveRiskSettings">
        保存配置
      </a-button>
      <a-button style="margin-left: 8px" size="large" @click="resetToDefaults">
        重置默认值
      </a-button>
    </div>

    <!-- 风控历史记录模态窗 -->
    <a-modal
      v-model:visible="riskHistoryVisible"
      title="风控触发历史"
      width="900px"
      :footer="null"
    >
      <a-table :columns="historyColumns" :data-source="riskHistoryData" :pagination="{ pageSize: 10 }">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'triggerType'">
            <a-tag :color="getTriggerTypeColor(record.triggerType)">
              {{ record.triggerType }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-tag :color="getActionColor(record.action)">
              {{ record.action }}
            </a-tag>
          </template>
        </template>
      </a-table>
    </a-modal>

    <!-- 时间点设置模态框 -->
    <a-modal
      v-model:visible="timePointsModalVisible"
      title="重要时间点管理"
      width="800px"
      @ok="saveTimePoints"
      @cancel="timePointsModalVisible = false"
      okText="保存"
      cancelText="取消"
    >
      <div class="time-points-container">
        <a-table 
          :dataSource="timeRiskForm.forbiddenTimePoints" 
          :columns="timePointsColumns"
          :pagination="false"
          rowKey="id"
          size="middle"
          :bordered="true"
        >
          <template #headerCell="{ column }">
            <template v-if="column.key === 'name'">
              <span>名称</span>
            </template>
            <template v-if="column.key === 'timeType'">
              <span>类型</span>
            </template>
            <template v-if="column.key === 'startTime'">
              <span>
                开始时间
                <a-tooltip placement="top">
                  <template #title>禁止交易的开始时间</template>
                  <question-circle-outlined style="margin-left: 4px" />
                </a-tooltip>
              </span>
            </template>
            <template v-if="column.key === 'endTime'">
              <span>
                结束时间
                <a-tooltip placement="top">
                  <template #title>禁止交易的结束时间，永久类型仅需设置时间</template>
                  <question-circle-outlined style="margin-left: 4px" />
                </a-tooltip>
              </span>
            </template>
          </template>
          
          <template #bodyCell="{ column, record, index }">
            <!-- 名称列 -->
            <template v-if="column.key === 'name'">
              <a-input 
                v-model:value="record.name" 
                placeholder="名称，如'非农数据'" 
                style="width: 100%"
              />
            </template>
            
            <!-- 时间类型列 -->
            <template v-if="column.key === 'timeType'">
              <a-select 
                v-model:value="record.timeType" 
                style="width: 100%"
              >
                <a-select-option value="oneTime">一次性</a-select-option>
                <a-select-option value="permanent">永久</a-select-option>
              </a-select>
            </template>
            
            <!-- 开始时间列 -->
            <template v-if="column.key === 'startTime'">
              <div class="time-inputs">
                <a-date-picker 
                  v-model:value="record.startDate" 
                  style="width: 55%"
                  v-if="record.timeType === 'oneTime'"
                />
                <a-time-picker 
                  v-model:value="record.startTime" 
                  format="HH:mm" 
                  :style="{ width: record.timeType === 'oneTime' ? '45%' : '100%' }"
                />
              </div>
            </template>
            
            <!-- 结束时间列 -->
            <template v-if="column.key === 'endTime'">
              <div class="time-inputs" v-if="record.timeType === 'oneTime'">
                <a-date-picker 
                  v-model:value="record.endDate" 
                  style="width: 55%"
                />
                <a-time-picker 
                  v-model:value="record.endTime" 
                  format="HH:mm" 
                  style="width: 45%"
                />
              </div>
              <div v-else>
                -
              </div>
            </template>
            
            <!-- 操作列 -->
            <template v-if="column.key === 'action'">
              <a-button 
                type="link" 
                danger 
                size="small" 
                @click="deleteTimePoint(index)"
              >
                删除
              </a-button>
            </template>
          </template>
        </a-table>

        <div class="time-points-empty" v-if="timeRiskForm.forbiddenTimePoints.length === 0">
          <a-empty description="暂无设置的时间点">
            <template #image>
              <img src="https://gw.alipayobjects.com/zos/antfincdn/ZHrcdLPrvN/empty.svg" style="height: 60px;" />
            </template>
          </a-empty>
        </div>
        
        <!-- 添加新时间点按钮 -->
        <div class="add-time-point" style="margin-top: 16px;">
          <a-button type="dashed" @click="addNewTimePoint" style="width: 100%">
            <template #icon><PlusOutlined /></template>
            添加时间点
          </a-button>
        </div>

        <div class="time-points-info" v-if="timeRiskForm.forbiddenTimePoints.length > 0">
          <a-alert type="info" show-icon style="margin-top: 16px;">
            <template #message>
              <div>
                <p>在设置的时间范围内将禁止交易</p>
                <p>永久类型的时间点会在每天指定时间段内禁止交易</p>
              </div>
            </template>
          </a-alert>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { message, Modal } from 'ant-design-vue';
import { 
  StopOutlined, 
  HistoryOutlined,
  ExclamationCircleOutlined,
  QuestionCircleOutlined,
  PlusOutlined
} from '@ant-design/icons-vue';
import dayjs from 'dayjs';

// 活跃策略数量
const activeStrategies = ref(6);
const totalStrategies = ref(10);
const activeStrategiesText = computed(() => `${activeStrategies.value}/${totalStrategies.value}`);

// 系统级风控条件
// 最大持仓币种设置
const maxPositionCoins = ref(10); // 默认最大持仓10个币种
const activePositions = ref(4); // 默认当前持仓4个

// 最大持仓价值设置
const maxPositionValue = ref(0); // 默认不限制持仓价值
const totalPositionValue = ref(20000); // 默认当前持仓价值

// 最大亏损停止设置
const maxLossCutoff = ref(0); // 默认不启用最大亏损停止
const currentMaxLoss = ref(200); // 当前最大亏损

// 账户安全风控表单
const accountRiskForm = reactive({
  lossLimit: 500,
  timeUnit: 'day'
});

// 市场风险风控表单
const marketRiskForm = reactive({
  priceVolatilityMonitoring: true,
  volatilityThreshold: 3.0,
  volatilityTimeWindow: 15,
  volatilityTimeUnit: 'minute',
  volatilityCalculationMethod: 'highLow',
  liquidityMonitoring: true,
  maxAllowedSlippage: 1.0
});

// 技术风控表单
const techRiskForm = reactive({
  apiTimeoutMonitoring: true,
  apiTimeoutThreshold: 2000,
  exchangeConnMonitoring: true,
  autoReconnectAttempts: 3,
  apiTimeoutCount: 0,
  networkErrors: 0
});

// 时间风控表单
interface TimePoint {
  id: number;
  name: string;
  description: string;
  timeType: string;
  startDate?: dayjs.Dayjs;
  startTime?: dayjs.Dayjs;
  endDate?: dayjs.Dayjs;
  endTime?: dayjs.Dayjs;
}

const timeRiskForm = reactive({
  tradingTimeLimit: false,
  tradingDays: ['1', '2', '3', '4', '5'], // 工作日
  tradingStartTime: dayjs('09:00:00', 'HH:mm:ss'),
  tradingEndTime: dayjs('21:00:00', 'HH:mm:ss'),
  timePointLimit: false,
  forbiddenTimePoints: [] as TimePoint[]
});

// 风控历史记录
const riskHistoryVisible = ref(false);
const historyColumns = [
  { title: '时间', dataIndex: 'time', key: 'time' },
  { title: '触发类型', dataIndex: 'triggerType', key: 'triggerType' },
  { title: '触发值', dataIndex: 'triggerValue', key: 'triggerValue' },
  { title: '阈值', dataIndex: 'threshold', key: 'threshold' },
  { title: '采取动作', dataIndex: 'action', key: 'action' },
  { title: '影响范围', dataIndex: 'affectedScope', key: 'affectedScope' }
];

const riskHistoryData = [
  {
    id: 1,
    time: '2023-12-20 09:45:23',
    triggerType: '单日亏损限制',
    triggerValue: '521 USDT',
    threshold: '500 USDT',
    action: '暂停所有策略',
    affectedScope: '全部'
  },
  {
    id: 2,
    time: '2023-12-19 15:20:37',
    triggerType: 'API响应超时',
    triggerValue: '3500 毫秒',
    threshold: '2000 毫秒',
    action: '暂停币安交易',
    affectedScope: '币安'
  },
  {
    id: 3,
    time: '2023-12-18 13:12:05',
    triggerType: '价格异常波动',
    triggerValue: '4.8%',
    threshold: '3.0%',
    action: '暂停BTC相关策略',
    affectedScope: 'BTC交易对'
  }
];

// 获取触发类型标签颜色
const getTriggerTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    '单日亏损限制': 'red',
    'API响应超时': 'orange',
    '价格异常波动': 'gold'
  };
  return colors[type] || 'blue';
};

// 获取动作标签颜色
const getActionColor = (action: string) => {
  if (action.includes('暂停')) return 'orange';
  if (action.includes('停止')) return 'red';
  if (action.includes('警告')) return 'gold';
  return 'blue';
};

// 紧急停止所有交易
const emergencyStopAll = () => {
  message.success('已紧急停止所有交易策略');
};

// 显示风控历史
const showRiskHistory = () => {
  riskHistoryVisible.value = true;
};

// 保存风控设置
const saveRiskSettings = () => {
  // 这里可以添加保存到后端的逻辑
  message.success('风控配置已保存');
};

// 重置默认值
const resetToDefaults = () => {
  // 重置所有表单到默认值
  Object.assign(accountRiskForm, {
    lossLimit: 500,
    timeUnit: 'day'
  });
  
  Object.assign(marketRiskForm, {
    priceVolatilityMonitoring: true,
    volatilityThreshold: 3.0,
    volatilityTimeWindow: 15,
    volatilityTimeUnit: 'minute',
    volatilityCalculationMethod: 'highLow',
    liquidityMonitoring: true,
    maxAllowedSlippage: 1.0
  });
  
  Object.assign(techRiskForm, {
    apiTimeoutMonitoring: true,
    apiTimeoutThreshold: 2000,
    exchangeConnMonitoring: true,
    autoReconnectAttempts: 3
  });

  // 重置时间风控表单
  Object.assign(timeRiskForm, {
    tradingTimeLimit: false,
    tradingDays: ['1', '2', '3', '4', '5'],
    tradingStartTime: dayjs('09:00:00', 'HH:mm:ss'),
    tradingEndTime: dayjs('21:00:00', 'HH:mm:ss'),
    timePointLimit: false,
    forbiddenTimePoints: []
  });
  
  // 重置系统级风控条件
  maxPositionCoins.value = 10;
  maxPositionValue.value = 0;
  maxLossCutoff.value = 0;
  
  message.success('已重置为默认配置');
};

// 显示时间点设置模态框
const timePointsModalVisible = ref(false);
const showTimePointsModal = () => {
  timePointsModalVisible.value = true;
};

// 处理最大持仓币种数变更
const handleMaxPositionsChange = (value: number) => {
  maxPositionCoins.value = value;
  // 实际环境中这里应该调用API保存设置
  message.success(`已设置最大持仓币种数为: ${value === 0 ? '无限制' : value}`);
};

// 处理最大持仓价值变更
const handleMaxPositionValueChange = (value: number) => {
  maxPositionValue.value = value;
  // 实际环境中这里应该调用API保存设置
  message.success(`已设置最大持仓价值为: ${value === 0 ? '无限制' : value + ' USDT'}`);
};

// 处理最大亏损停止变更
const handleMaxLossCutoffChange = (value: number) => {
  maxLossCutoff.value = value;
  // 实际环境中这里应该调用API保存设置
  message.success(`已设置最大亏损停止为: ${value === 0 ? '无限制' : value + ' USDT'}`);
};

// 页面加载时获取数据
onMounted(() => {
  // 这里可以添加获取数据的逻辑
});

// 声明时间点表格列
const timePointsColumns = [
  { title: '名称', dataIndex: 'name', key: 'name', width: '20%' },
  { title: '类型', dataIndex: 'timeType', key: 'timeType', width: '15%' },
  { title: '开始时间', dataIndex: 'startTime', key: 'startTime', width: '25%' },
  { title: '结束时间', dataIndex: 'endTime', key: 'endTime', width: '25%' },
  { title: '操作', key: 'action', width: '15%' }
];

// 添加新时间点
const addNewTimePoint = () => {
  const newTimePoint: TimePoint = {
    id: Date.now(), // 使用时间戳作为临时ID
    name: '',
    description: '',
    timeType: 'oneTime',
    startDate: dayjs(),
    startTime: dayjs(),
    endDate: dayjs().add(1, 'hour'),
    endTime: dayjs().add(1, 'hour')
  };
  
  // 添加新时间点
  timeRiskForm.forbiddenTimePoints.push(newTimePoint);
};

// 删除时间点
const deleteTimePoint = (index: number) => {
  Modal.confirm({
    title: '删除确认',
    content: '确定要删除这个时间点吗？',
    okText: '确定',
    cancelText: '取消',
    onOk: () => {
      timeRiskForm.forbiddenTimePoints.splice(index, 1);
      message.success('已删除时间点');
    }
  });
};

// 保存时间点设置
const saveTimePoints = () => {
  // 验证所有时间点是否都有名称
  const invalidTimePoints = timeRiskForm.forbiddenTimePoints.filter(point => !point.name);
  if (invalidTimePoints.length > 0) {
    message.error('请为所有时间点设置名称');
    return;
  }
  
  // 在实际应用中这里应该调用API保存设置
  message.success('时间点设置已保存');
  timePointsModalVisible.value = false;
};

// 添加格式化时间点显示的函数
const formatTimePointDisplay = (timePoint: TimePoint) => {
  if (timePoint.timeType === 'oneTime') {
    return `${dayjs(timePoint.startDate).format('YYYY-MM-DD')} ${dayjs(timePoint.startTime).format('HH:mm')} - 
            ${dayjs(timePoint.endDate).format('YYYY-MM-DD')} ${dayjs(timePoint.endTime).format('HH:mm')}`;
  } else {
    return dayjs(timePoint.startTime).format('HH:mm');
  }
};
</script>

<style scoped>
.risk-management {
  padding: 24px;
  background-color: #f0f2f5;
}

.page-header-container {
  margin-bottom: 16px;
}

.header-card {
  box-shadow: 0 1px 2px -2px rgba(0, 0, 0, 0.16),
              0 3px 6px 0 rgba(0, 0, 0, 0.12),
              0 5px 12px 4px rgba(0, 0, 0, 0.09);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.risk-card {
  margin-bottom: 24px;
  border-radius: 8px;
  box-shadow: 0 1px 2px -2px rgba(0, 0, 0, 0.16),
              0 3px 6px 0 rgba(0, 0, 0, 0.12),
              0 5px 12px 4px rgba(0, 0, 0, 0.09);
}

.risk-condition-card {
  height: 100%;
  border-radius: 4px;
  background-color: #fafafa;
  border: 1px solid #f0f0f0;
}

.risk-status {
  margin-top: 12px;
  font-size: 13px;
}

.risk-indicator {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
  color: rgba(0, 0, 0, 0.65);
}

.active-value {
  font-weight: 500;
  margin-left: 4px;
}

.input-with-select {
  display: flex;
}

.form-item-help {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
  line-height: 1.5;
  margin-top: 4px;
}

.risk-actions {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  margin-bottom: 48px;
}

:deep(.ant-card-head) {
  font-weight: 600;
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.ant-table-thead > tr > th) {
  background-color: #fafafa;
  font-weight: 600;
}

:deep(.ant-form-item-label > label) {
  font-weight: 500;
}
</style> 