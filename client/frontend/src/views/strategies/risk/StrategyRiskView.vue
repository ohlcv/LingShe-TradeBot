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
          <div class="step-item clickable" @click="goToStep('params')">
            <check-circle-outlined class="step-icon completed" />
            <span class="step-text">策略参数</span>
          </div>
          <div class="step-divider"></div>
          <div class="step-item active">
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

      <h1 class="page-title">风控配置</h1>
      
      <a-form
        :model="riskForm"
        ref="formRef"
        layout="vertical"
        class="strategy-form"
      >
        <a-card class="settings-card" title="资金风控">
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item name="totalLossLimit">
                <div class="label-with-tooltip">
                  <span>总亏损停止阈值</span>
                  <a-tooltip placement="top">
                    <template #title>策略总亏损达到该金额时自动停止</template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </div>
                <a-input-number 
                  v-model:value="riskForm.totalLossLimit" 
                  :min="1" 
                  :step="1" 
                  style="width: 100%" 
                  addon-after="USDT" 
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item name="totalProfitLimit">
                <div class="label-with-tooltip">
                  <span>总盈利停止阈值</span>
                  <a-tooltip placement="top">
                    <template #title>策略总盈利达到该金额时自动停止</template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </div>
                <a-input-number 
                  v-model:value="riskForm.totalProfitLimit" 
                  :min="1" 
                  :step="1" 
                  style="width: 100%" 
                  addon-after="USDT" 
                />
              </a-form-item>
            </a-col>
          </a-row>
          
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item name="maxLossPerTrade">
                <div class="label-with-tooltip">
                  <span>单笔最大亏损额</span>
                  <a-tooltip placement="top">
                    <template #title>单笔交易允许的最大亏损金额</template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </div>
                <a-input-number 
                  v-model:value="riskForm.maxLossPerTrade" 
                  :min="1" 
                  :step="1" 
                  style="width: 100%" 
                  addon-after="USDT" 
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item name="maxPosition">
                <div class="label-with-tooltip">
                  <span>最大持仓金额</span>
                  <a-tooltip placement="top">
                    <template #title>策略允许的最大持仓金额</template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </div>
                <a-input-number 
                  v-model:value="riskForm.maxPosition" 
                  :min="1" 
                  :step="1" 
                  style="width: 100%" 
                  addon-after="USDT" 
                />
              </a-form-item>
            </a-col>
          </a-row>
        </a-card>
        
        <a-card class="settings-card" title="时间风控" style="margin-top: 16px;">
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item name="tradingTimeLimit">
                <div class="label-with-tooltip">
                  <span>交易时间限制</span>
                  <a-tooltip placement="top">
                    <template #title>启用后将只在指定时段内进行交易</template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </div>
                <a-switch v-model:checked="riskForm.tradingTimeLimit" />
                <div class="form-item-help">仅在特定时间段内允许交易</div>
              </a-form-item>
            </a-col>
            <a-col :span="12" v-if="riskForm.tradingTimeLimit">
              <a-form-item name="tradingStartTime">
                <div class="label-with-tooltip">
                  <span>交易开始时间</span>
                </div>
                <a-time-picker 
                  v-model:value="riskForm.tradingStartTime" 
                  format="HH:mm:ss"
                  style="width: 100%" 
                />
                <div class="form-item-help">每日交易开始时间</div>
              </a-form-item>
            </a-col>
            <a-col :span="12" v-if="riskForm.tradingTimeLimit">
              <a-form-item name="tradingEndTime">
                <div class="label-with-tooltip">
                  <span>交易结束时间</span>
                </div>
                <a-time-picker 
                  v-model:value="riskForm.tradingEndTime" 
                  format="HH:mm:ss"
                  style="width: 100%" 
                />
                <div class="form-item-help">每日交易结束时间</div>
              </a-form-item>
            </a-col>
          </a-row>
          
          <a-divider />
          
          <a-row :gutter="24">
            <a-col :span="24">
              <a-form-item name="timePointLimit">
                <div class="label-with-tooltip">
                  <span>重要时间点禁止交易</span>
                  <a-tooltip placement="top">
                    <template #title>启用后将在特定时间点禁止交易</template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </div>
                <a-switch v-model:checked="riskForm.timePointLimit" />
              </a-form-item>
            </a-col>
          </a-row>
          
          <a-row :gutter="24" v-if="riskForm.timePointLimit">
            <a-col :span="24">
              <a-form-item label="重要时间点设置" name="forbiddenTimePoints">
                <a-button 
                  type="dashed" 
                  style="width: 100%"
                  @click="showTimePointsModal"
                >
                  <template #icon><PlusOutlined /></template>
                  添加/管理时间点
                </a-button>
                <div class="form-item-help">已设置 {{riskForm.forbiddenTimePoints.length}} 个重要时间点</div>
              </a-form-item>
            </a-col>
          </a-row>
        </a-card>
        
        <a-card class="settings-card" title="交易保护" style="margin-top: 16px;">
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item name="consecutiveLossLimit">
                <div class="label-with-tooltip">
                  <span>连续亏损限制</span>
                  <a-tooltip placement="top">
                    <template #title>连续亏损达到设定次数后暂停交易</template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </div>
                <a-input-number 
                  v-model:value="riskForm.consecutiveLossLimit" 
                  :min="1" 
                  :step="1" 
                  style="width: 100%" 
                  placeholder="设置连续亏损次数限制" 
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item name="consecutiveLossWindow">
                <div class="label-with-tooltip">
                  <span>连续亏损时间窗口</span>
                  <a-tooltip placement="top">
                    <template #title>计算连续亏损的时间范围</template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </div>
                <div class="input-with-select">
                  <a-input-number
                    v-model:value="riskForm.consecutiveLossWindow"
                    :min="1"
                    :step="1"
                    style="width: 70%"
                    placeholder="设置时间窗口"
                  />
                  <a-select
                    v-model:value="riskForm.consecutiveLossWindowUnit"
                    style="width: 30%"
                  >
                    <a-select-option value="minutes">分钟</a-select-option>
                    <a-select-option value="hours">小时</a-select-option>
                    <a-select-option value="days">天</a-select-option>
                  </a-select>
                </div>
              </a-form-item>
            </a-col>
          </a-row>
          
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item name="orderFrequencyLimit">
                <div class="label-with-tooltip">
                  <span>下单频率限制</span>
                  <a-tooltip placement="top">
                    <template #title>限制每个时间单位内允许下单的最大数量</template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </div>
                <div class="input-with-select">
                  <a-input-number
                    v-model:value="riskForm.orderFrequencyLimit"
                    :min="1"
                    :step="1"
                    style="width: 70%"
                    placeholder="设置订单数量限制"
                  />
                  <a-select
                    v-model:value="riskForm.orderFrequencyLimitUnit"
                    style="width: 30%"
                  >
                    <a-select-option value="minutes">分钟</a-select-option>
                    <a-select-option value="hours">小时</a-select-option>
                    <a-select-option value="days">天</a-select-option>
                  </a-select>
                </div>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item name="minOrderInterval">
                <div class="label-with-tooltip">
                  <span>最小下单间隔</span>
                  <a-tooltip placement="top">
                    <template #title>两次下单之间需要等待的最小时间间隔</template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </div>
                <div class="input-with-select">
                  <a-input-number
                    v-model:value="riskForm.minOrderInterval"
                    :min="1"
                    :step="1"
                    style="width: 70%"
                    placeholder="设置最小时间间隔"
                  />
                  <a-select
                    v-model:value="riskForm.minOrderIntervalUnit"
                    style="width: 30%"
                  >
                    <a-select-option value="minutes">分钟</a-select-option>
                    <a-select-option value="hours">小时</a-select-option>
                    <a-select-option value="days">天</a-select-option>
                  </a-select>
                </div>
              </a-form-item>
            </a-col>
          </a-row>
          
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item name="slippageThreshold">
                <div class="label-with-tooltip">
                  <span>滑点保护阈值</span>
                  <a-tooltip placement="top">
                    <template #title>即将推出：当市场滑点超过该阈值时暂停交易</template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </div>
                <a-input-number
                  v-model:value="riskForm.slippageThreshold"
                  :min="0"
                  :step="0.1"
                  style="width: 100%"
                  placeholder="敬请期待"
                  disabled
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item name="volatilityThreshold">
                <div class="label-with-tooltip">
                  <span>异常波动暂停阈值</span>
                  <a-tooltip placement="top">
                    <template #title>即将推出：当市场波动率超过该阈值时暂停交易</template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </div>
                <a-input-number
                  v-model:value="riskForm.volatilityThreshold"
                  :min="0"
                  :step="0.1"
                  style="width: 100%"
                  placeholder="敬请期待"
                  disabled
                />
              </a-form-item>
            </a-col>
          </a-row>
        </a-card>

        <div class="step-actions">
          <a-space>
            <a-button @click="goBack">
              上一步
            </a-button>
            <a-button type="primary" @click="submitForm">
              下一步
            </a-button>
          </a-space>
        </div>
      </a-form>
    </a-card>
    
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
          :dataSource="riskForm.forbiddenTimePoints" 
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

        <div class="time-points-empty" v-if="riskForm.forbiddenTimePoints.length === 0">
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

        <div class="time-points-info" v-if="riskForm.forbiddenTimePoints.length > 0">
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
import { ref, reactive, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { message, Modal } from 'ant-design-vue';
import dayjs from 'dayjs';
import { 
  QuestionCircleOutlined,
  CheckCircleOutlined,
  PlusOutlined
} from '@ant-design/icons-vue';
import type { FormInstance } from 'ant-design-vue/es/form';
import type { Dayjs } from 'dayjs';
import { useStrategyCreationStore } from '@/store/modules/strategyCreation';
import type { RiskConfig } from '@/store/modules/strategyCreation';

const router = useRouter();
const route = useRoute();
const formRef = ref<FormInstance>();
const strategyCreationStore = useStrategyCreationStore();

// 从URL获取基础参数
const strategyType = route.query.strategyType as string;
const strategyName = route.query.strategyName as string;

// 初始化表单数据
const riskForm = reactive({
  // 资金风控
  totalLossLimit: 0,
  totalProfitLimit: 0,
  maxLossPerTrade: 0,
  maxPosition: 0,
  
  // 时间风控
  tradingTimeLimit: false,
  tradingStartTime: null as Dayjs | null,
  tradingEndTime: null as Dayjs | null,
  timePointLimit: false,
  forbiddenTimePoints: [] as TimePoint[],
  
  // 交易保护
  consecutiveLossLimit: 0,
  consecutiveLossWindow: 0,
  consecutiveLossWindowUnit: 'hour',
  orderFrequencyLimit: 0,
  orderFrequencyLimitUnit: 'hour',
  minOrderInterval: 0,
  minOrderIntervalUnit: 'minute',
  slippageThreshold: 0,
  volatilityThreshold: 0
});

// 时间点数据结构
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

// 时间点管理模态框
const timePointsModalVisible = ref(false);
const showTimePointsModal = () => {
  timePointsModalVisible.value = true;
};

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
    id: Date.now(),
    name: '',
    description: '',
    timeType: 'oneTime',
    startDate: dayjs(),
    startTime: dayjs(),
    endDate: dayjs().add(1, 'hour'),
    endTime: dayjs().add(1, 'hour')
  };
  
  riskForm.forbiddenTimePoints.push(newTimePoint);
};

// 删除时间点
const deleteTimePoint = (index: number) => {
  Modal.confirm({
    title: '删除确认',
    content: '确定要删除这个时间点吗？',
    okText: '确定',
    cancelText: '取消',
    onOk: () => {
      riskForm.forbiddenTimePoints.splice(index, 1);
      message.success('已删除时间点');
    }
  });
};

// 保存时间点设置
const saveTimePoints = () => {
  // 验证所有时间点是否都有名称
  const invalidTimePoints = riskForm.forbiddenTimePoints.filter(point => !point.name);
  if (invalidTimePoints.length > 0) {
    message.error('请为所有时间点设置名称');
    return;
  }
  
  message.success('时间点设置已保存');
  timePointsModalVisible.value = false;
};

// 提交表单
const submitForm = async () => {
  try {
    await formRef.value?.validate();
    
    // 构建风控配置对象
    const riskConfig: RiskConfig = {
      totalLossLimit: riskForm.totalLossLimit,
      totalProfitLimit: riskForm.totalProfitLimit,
      maxLossPerTrade: riskForm.maxLossPerTrade,
      maxPosition: riskForm.maxPosition,
      tradingTimeLimit: riskForm.tradingTimeLimit,
      tradingStartTime: riskForm.tradingStartTime?.format('HH:mm'),
      tradingEndTime: riskForm.tradingEndTime?.format('HH:mm')
    };
    
    // 保存到store
    strategyCreationStore.setRiskConfig(riskConfig);
    
    // 导航到完成页面
    router.push('/strategies/create/finish');
    
  } catch (error) {
    message.error('请完善表单信息');
  }
};

// 导航到上一步
const goBack = () => {
  // 根据策略类型决定上一步的URL
  let prevStep = 'params';
  if (strategyCreationStore.strategyType === 'grid') {
    prevStep = 'grid';
  } else if (strategyCreationStore.strategyType === 'trend') {
    prevStep = 'trend';
  } else if (strategyCreationStore.strategyType === 'tv') {
    prevStep = 'tv';
  }
  
  router.push(`/strategies/create/${prevStep}`);
};

// 导航到指定步骤
const goToStep = (step: string) => {
  let targetPath = `/strategies/create/${step}`;
  
  // 根据策略类型和步骤确定正确的目标路径
  if (step === 'params') {
    if (strategyCreationStore.strategyType === 'grid') {
      targetPath = '/strategies/create/grid';
    } else if (strategyCreationStore.strategyType === 'trend') {
      targetPath = '/strategies/create/trend';
    } else if (strategyCreationStore.strategyType === 'tv') {
      targetPath = '/strategies/create/tv';
    }
  }
  
  router.push(targetPath);
};

// 组件挂载时从URL参数中恢复之前的配置
onMounted(() => {
  // 从URL中恢复之前的配置
  if (route.query.riskConfig) {
    try {
      const savedConfig = JSON.parse(route.query.riskConfig as string);
      
      // 合并已保存的配置到表单中
      Object.keys(savedConfig).forEach(key => {
        if (key === 'tradingStartTime' && savedConfig[key]) {
          riskForm.tradingStartTime = dayjs(savedConfig[key], 'HH:mm');
        } else if (key === 'tradingEndTime' && savedConfig[key]) {
          riskForm.tradingEndTime = dayjs(savedConfig[key], 'HH:mm');
        } else if (riskForm.hasOwnProperty(key)) {
          // @ts-ignore
          riskForm[key] = savedConfig[key];
        }
      });
    } catch (error) {
      // 解析错误，使用默认配置
      console.error('解析风控配置失败', error);
    }
  }
});
</script>

<style scoped>
.strategy-view {
  width: 100%;
  background-color: #f0f2f5;
  margin: 0;
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
  cursor: pointer;
  margin-right: 8px;
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
  width: 24px;
  height: 24px;
  line-height: 24px;
  border-radius: 50%;
  background-color: rgba(24, 144, 255, 0.1);
  color: #1890ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
}

.step-text {
  font-size: 14px;
}

.step-item.active .step-text {
  color: #1890ff;
  font-weight: 500;
}

.step-item.clickable:hover {
  background-color: rgba(24, 144, 255, 0.05);
  border-radius: 4px;
  padding: 2px 4px;
  margin: -2px 4px -2px -4px;
  transition: all 0.3s;
}

.page-title {
  font-size: 18px;
  font-weight: 700;
  margin: 16px 0 24px 0;
  padding: 0;
}

.card-title {
  padding: 16px 0;
}

.card-title h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  padding-bottom: 16px;
}

.nav-steps {
  display: none;
}

.settings-card {
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 5px rgba(0,0,0,0.05);
  transition: all 0.3s;
}

.settings-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.form-hint {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
  line-height: 1.5;
}

.step-actions {
  margin-top: 24px;
  text-align: center;
}

.clickable-step:hover {
  color: #40a9ff;
  text-decoration: underline;
}

:deep(.ant-form-item-label) {
  font-weight: 500;
}

:deep(.ant-card-head) {
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
  padding: 0 16px;
}

:deep(.ant-card-head-title) {
  font-weight: 600;
  font-size: 16px;
}

:deep(.ant-divider) {
  margin: 16px 0;
}

:deep(.ant-switch-checked) {
  background-color: #52c41a;
}

:deep(.ant-btn) {
  border-radius: 4px;
  transition: all 0.3s;
}

:deep(.ant-btn:hover) {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

:deep(.ant-input-number) {
  border-radius: 4px;
}

:deep(.ant-select) {
  border-radius: 4px;
}

:deep(.ant-time-picker) {
  border-radius: 4px;
}

:deep(.ant-checkbox-wrapper) {
  margin-right: 12px;
  margin-bottom: 8px;
}

.input-with-select {
  display: flex;
  align-items: center;
}

.input-with-select .ant-input-number {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.input-with-select .ant-select .ant-select-selector {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  height: 100%;
  display: flex;
  align-items: center;
}

.label-with-tooltip {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

/* 卡片样式重置 */
:deep(.ant-card) {
  margin: 0;
  border-radius: 0;
}

:deep(.ant-card-head) {
  padding: 0 16px;
}

:deep(.ant-card-body) {
  padding: 16px;
}

/* 添加时间点相关样式 */
.form-item-help {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
  line-height: 1.5;
  margin-top: 4px;
}

.time-inputs {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.time-points-container {
  max-height: 60vh;
  overflow-y: auto;
}
</style> 