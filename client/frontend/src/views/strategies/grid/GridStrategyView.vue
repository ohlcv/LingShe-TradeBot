<template>
  <div class="strategy-view">
    <a-card :bordered="false">
      <template #title>
        <div class="strategy-steps">
          <div class="step-item" @click="goToStep('basic')">
            <check-circle-outlined class="step-icon completed" />
            <span class="step-text">基本设置</span>
          </div>
          <div class="step-divider"></div>
          <div class="step-item active">
            <div class="step-number">2</div>
            <span class="step-text">策略参数</span>
          </div>
          <div class="step-divider"></div>
          <div class="step-item" @click="goToStep('risk')">
            <div class="step-number">3</div>
            <span class="step-text">风控配置</span>
          </div>
          <div class="step-divider"></div>
          <div class="step-item" @click="goToStep('finish')">
            <div class="step-number">4</div>
            <span class="step-text">完成</span>
          </div>
        </div>
      </template>

      <h1 class="page-title">网格策略设置</h1>

      <!-- 网格策略表单 -->
      <a-form
        :model="gridForm"
        :rules="gridRules"
        ref="formRef"
        layout="vertical"
        class="strategy-form"
      >
        <!-- 网格层级设置 -->
        <a-card class="config-card" style="margin-top: 16px; box-shadow: 0 1px 5px rgba(0,0,0,0.05);">
          <template #title>
            <div style="width: 100%; text-align: center; display: flex; justify-content: center; align-items: center;">
              <h2 style="margin: 0; font-weight: 600; font-size: 18px;">网格层级设置</h2>
              <a-tooltip placement="right">
                <template #title>
                  <div>
                    灰色背景单元格表示已开仓和待止盈状态的网格层，这些层已被锁定为只读状态，不可编辑或删除
                  </div>
                </template>
                <question-circle-outlined style="font-size: 16px; color: #333; padding: 2px; margin-left: 8px;" />
              </a-tooltip>
            </div>
          </template>
          
          <a-row :gutter="24" style="margin-bottom: 16px; padding: 8px; background-color: #f8f9fa; border-radius: 4px;">
            <a-col :span="8">
              <a-form-item label="投资张数" name="investment">
                <a-input-number
                  v-model:value="gridForm.investment"
                  style="width: 100%"
                  :min="1"
                  :step="1"
                  :precision="0"
                  placeholder="请输入投资张数"
                />
              </a-form-item>
            </a-col>
            
            <a-col :span="8">
              <a-form-item label="网格数量" name="gridCount">
                <a-input-number
                  v-model:value="gridForm.gridCount"
                  style="width: 100%"
                  :min="2"
                  :max="50"
                  placeholder="请输入网格数量"
                />
              </a-form-item>
            </a-col>
            
            <a-col :span="8">
              <a-form-item label=" " style="margin-top: 5px;">
                <a-button type="primary" @click="generateGridLevels" style="width: 100%;">
                  <template #icon><SettingOutlined /></template>
                  自动生成网格层级
                </a-button>
              </a-form-item>
            </a-col>
          </a-row>

          <a-table
            :dataSource="gridLevels"
            :columns="gridLevelColumns"
            :pagination="false"
            :rowClassName="(record: GridLevel) => (record.status === '已开仓' || record.status === '待止盈') ? 'readonly-row' : ''"
            :bordered="true"
            size="small"
          >
            <template #headerCell="{ column }">
              <template v-if="column.dataIndex === 'level'">
                <span>
                  层级
                </span>
              </template>
              
              <template v-if="column.dataIndex === 'status'">
                <span>
                  状态
                  <a-tooltip placement="top">
                    <template #title>
                      <div>
                        <div>"已开仓"(已成交的买入订单)</div>
                        <div>"待止盈"(当前持仓中等待卖出)</div>
                        <div>"待开仓"(包含当前价格的层级)</div>
                        <div>"未开仓"(尚未触发的层级)</div>
                      </div>
                    </template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </span>
              </template>
              
              <template v-if="column.dataIndex === 'openRatio'">
                <span>
                  开仓比例(%)
                  <a-tooltip placement="top">
                    <template #title>开仓比例决定买入订单的数量占比</template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </span>
              </template>
              
              <template v-if="column.dataIndex === 'openReboundRatio'">
                <span>
                  开仓反弹比例(%)
                  <a-tooltip placement="top">
                    <template #title>开仓反弹比例用于设置开仓的执行条件，防止追涨</template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </span>
              </template>
              
              <template v-if="column.dataIndex === 'takeProfit'">
                <span>
                  止盈
                  <a-tooltip placement="top">
                    <template #title>
                      <div>
                        <div>支持多层分批止盈，防止杀跌，提高成交价格质量</div>
                        <div>止盈比例：达到该比例时触发止盈条件</div>
                        <div>回调比例：价格从最高点回调多少比例时执行止盈</div>
                        <div>平仓比例：触发该止盈层级时平掉的仓位比例</div>
                      </div>
                    </template>
                    <question-circle-outlined style="margin-left: 4px" />
                  </a-tooltip>
                </span>
              </template>
            </template>
            
            <template #bodyCell="{ column, record }">
              <template v-if="column.dataIndex === 'size'">
                <a-input-number 
                  v-if="record.status !== '已开仓' && record.status !== '待止盈'" 
                  v-model:value="record.size" 
                  :precision="0" 
                  :min="1" 
                  :step="1" 
                  style="width: 60px" 
                />
                <span v-else>{{ record.size }}</span>
              </template>
              
              <template v-if="column.dataIndex === 'openRatio'">
                <a-input-number 
                  v-if="record.status !== '已开仓' && record.status !== '待止盈'" 
                  v-model:value="record.openRatio" 
                  :precision="1" 
                  :min="0.1" 
                  :step="0.1" 
                  style="width: 80px" 
                />
                <span v-else>{{ record.openRatio }}</span>
              </template>
              
              <template v-if="column.dataIndex === 'openReboundRatio'">
                <a-input-number 
                  v-if="record.status !== '已开仓' && record.status !== '待止盈'" 
                  v-model:value="record.openReboundRatio" 
                  :precision="1" 
                  :min="0.1" 
                  :step="0.1" 
                  style="width: 80px" 
                />
                <span v-else>{{ record.openReboundRatio }}</span>
              </template>
              
              <template v-if="column.dataIndex === 'takeProfit'">
                <div v-if="record.status !== '已开仓' && record.status !== '待止盈'">
                  <a-button 
                    type="link" 
                    size="small" 
                    @click="openTakeProfitModal(record)"
                  >
                    {{ hasMultipleTakeProfit(record) ? `${record.takeProfitLevels.length}层止盈` : '设置止盈' }}
                  </a-button>
                </div>
                <div v-else>
                  {{ hasMultipleTakeProfit(record) ? `${record.takeProfitLevels.length}层止盈` : 
                     record.takeProfitLevels.length > 0 ? `${record.takeProfitLevels[0].ratio}%` : '未设置' }}
                </div>
              </template>
              
              <template v-if="column.dataIndex === 'status'">
                <a-tag :color="getStatusColor(record.status)">{{ record.status }}</a-tag>
              </template>
              
              <template v-if="column.dataIndex === 'action'">
                <div v-if="record.status !== '已开仓' && record.status !== '待止盈'">
                  <a-button 
                    type="link" 
                    danger 
                    size="small" 
                    @click="deleteGridLevel(record)"
                  >
                    删除
                  </a-button>
                </div>
                <a-button 
                  v-else
                  type="link" 
                  size="small" 
                  @click="viewTransactionRecords(record)"
                >
                  <template #icon><clock-circle-outlined /></template>
                  交易记录
                </a-button>
              </template>
            </template>
          </a-table>
          
          <div style="margin-top: 16px;">
            <a-button type="dashed" block @click="addGridLevel" class="add-button">
              <template #icon><PlusOutlined /></template>
              添加网格层级
            </a-button>
          </div>
        </a-card>
        
        <!-- 总体持仓设置 -->
        <a-card class="config-card" style="margin-top: 16px; box-shadow: 0 1px 5px rgba(0,0,0,0.05);">
          <template #title>
            <div style="width: 100%; text-align: center; display: flex; justify-content: center; align-items: center;">
              <h2 style="margin: 0; font-weight: 600; font-size: 18px;">总体持仓设置</h2>
              <a-tooltip placement="right">
                <template #title>
                  <div>
                    总体持仓止盈基于当前平均持仓成本进行计算，触发条件满足时将平掉全部仓位
                  </div>
                </template>
                <question-circle-outlined style="font-size: 16px; color: #333; padding: 2px; margin-left: 8px;" />
              </a-tooltip>
            </div>
          </template>
          
          <a-row style="display: flex; align-items: center; justify-content: space-between; padding: 0 16px; margin-bottom: 16px;">
            <a-col :span="14">
              <div style="display: flex; align-items: center;">
                <span style="font-weight: 500; margin-right: 8px;">当前设置:</span>
                <a-tag v-if="hasGlobalTakeProfit()" color="success">
                  <template #icon><CheckCircleOutlined /></template>
                  已设置 {{ globalTakeProfitLength }}层分批止盈
                </a-tag>
                <a-tag v-else color="warning">
                  <template #icon><ExclamationCircleOutlined /></template>
                  未设置
                </a-tag>
              </div>
            </a-col>
            <a-col :span="10" style="text-align: right;">
              <a-button 
                type="primary" 
                @click="openGlobalTakeProfitModal"
              >
                <template #icon><SettingOutlined /></template>
                {{ hasGlobalTakeProfit() ? '修改总体止盈' : '设置总体止盈' }}
              </a-button>
            </a-col>
          </a-row>
          
          <div v-if="hasGlobalTakeProfit()" style="margin-top: 16px; border-top: 1px dashed #f0f0f0; padding-top: 16px;">
            <div class="stat-header">总体持仓概览</div>
            <a-row :gutter="16" style="margin-top: 16px;">
              <a-col :span="6">
                <div class="stat-card">
                  <div class="stat-title">当前持仓层数</div>
                  <div class="stat-value">{{ getCurrentPositionLevels() }}</div>
                </div>
              </a-col>
              <a-col :span="6">
                <div class="stat-card">
                  <div class="stat-title">总持仓张数</div>
                  <div class="stat-value">{{ getTotalPositionSize() }}</div>
                </div>
              </a-col>
              <a-col :span="6">
                <div class="stat-card">
                  <div class="stat-title">当前收益</div>
                  <div class="stat-value" :class="parseFloat(getCurrentProfit()) >= 0 ? 'positive' : 'negative'">
                    {{ getCurrentProfit() }}%
                  </div>
                </div>
              </a-col>
              <a-col :span="6">
                <div class="stat-card">
                  <div class="stat-title">总体止盈批次</div>
                  <div class="stat-value">{{ globalTakeProfitLength }}</div>
                </div>
              </a-col>
            </a-row>
          </div>
        </a-card>

        <div class="form-actions" style="margin-top: 24px; text-align: center;">
          <a-space>
            <a-button @click="goBack">
              <template #icon><ArrowLeftOutlined /></template>
              上一步
            </a-button>
            <a-button type="primary" @click="saveAndGoNext">
              下一步
              <template #icon><ArrowRightOutlined /></template>
            </a-button>
          </a-space>
        </div>
      </a-form>
    </a-card>
  </div>
  
  <!-- 止盈设置弹窗 -->
  <a-modal
    v-model:visible="takeProfitModalVisible"
    title="分批止盈设置"
    :width="700"
    @ok="saveTakeProfitSettings"
    @cancel="cancelTakeProfitSettings"
    okText="确定"
    cancelText="取消"
  >
    <div v-if="currentEditingGridLevel" class="take-profit-form">
      <div class="level-info" style="margin-bottom: 16px;">
        <div><strong>网格层级：</strong> {{ currentEditingGridLevel.level }}</div>
        <div><strong>当前状态：</strong> {{ currentEditingGridLevel.status }}</div>
      </div>

      <a-table
        :dataSource="tempTakeProfitLevels"
        :columns="takeProfitLevelColumns"
        :pagination="false"
        :bordered="true"
        size="small"
      >
        <template #headerCell="{ column }">
          <template v-if="column.dataIndex === 'level'">
            <span>批次</span>
          </template>
          
          <template v-if="column.dataIndex === 'status'">
            <span>状态</span>
          </template>
          
          <template v-if="column.dataIndex === 'ratio'">
            <span>
              止盈比例(%)
              <a-tooltip placement="top">
                <template #title>达到该比例时触发止盈条件</template>
                <question-circle-outlined style="margin-left: 4px" />
              </a-tooltip>
            </span>
          </template>
          
          <template v-if="column.dataIndex === 'reboundRatio'">
            <span>
              回调比例(%)
              <a-tooltip placement="top">
                <template #title>价格从最高点回调多少比例时执行止盈</template>
                <question-circle-outlined style="margin-left: 4px" />
              </a-tooltip>
            </span>
          </template>
          
          <template v-if="column.dataIndex === 'portion'">
            <span>
              平仓比例
              <a-tooltip placement="top">
                <template #title>触发该止盈批次时平掉的仓位比例（所有批次比例总和为100%）</template>
                <question-circle-outlined style="margin-left: 4px" />
              </a-tooltip>
            </span>
          </template>
        </template>
        
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'level'">
            <span>{{ record.level }}</span>
          </template>
          
          <template v-if="column.dataIndex === 'status'">
            <a-tag :color="getTakeProfitStatusColor(record.status)">{{ record.status || '未触发' }}</a-tag>
          </template>
          
          <template v-if="column.dataIndex === 'ratio'">
            <a-input-number 
              v-model:value="record.ratio" 
              :precision="1" 
              :min="0.1" 
              :step="0.1" 
              style="width: 100%" 
            />
          </template>
          
          <template v-if="column.dataIndex === 'reboundRatio'">
            <a-input-number 
              v-model:value="record.reboundRatio" 
              :precision="1" 
              :min="0.1" 
              :step="0.1" 
              style="width: 100%" 
            />
          </template>
          
          <template v-if="column.dataIndex === 'portion'">
            <a-input-number 
              v-model:value="record.portion" 
              :precision="0" 
              :min="1" 
              :max="100" 
              :step="5" 
              @change="updatePortionDistribution"
              style="width: 100%" 
              :formatter="(value: number) => `${value}%`"
              :parser="(value: string) => value ? value.replace('%', '') : value"
            />
          </template>
          
          <template v-if="column.dataIndex === 'action'">
            <a-button 
              type="link" 
              danger 
              size="small" 
              @click="deleteTakeProfitLevel(record)"
            >
              删除
            </a-button>
          </template>
        </template>
      </a-table>

      <div class="total-portion" style="margin-top: 8px; text-align: right;">
        <a-tag v-if="calculateTotalPortion() !== 100" color="error">总平仓比例必须等于100%</a-tag>
      </div>

      <div style="margin-top: 16px;">
        <a-button type="dashed" block @click="addTakeProfitLevel">
          <template #icon><plus-outlined /></template>
          添加止盈批次
        </a-button>
      </div>
    </div>
  </a-modal>
  
  <!-- 全局止盈设置弹窗 -->
  <a-modal
    v-model:visible="globalTakeProfitModalVisible"
    title="总体持仓止盈设置"
    :width="700"
    @ok="saveGlobalTakeProfitSettings"
    @cancel="cancelGlobalTakeProfitSettings"
    okText="确定"
    cancelText="取消"
  >
    <div class="take-profit-form">
      <div class="level-info" style="margin-bottom: 16px;">
        <div><strong>止盈说明：</strong>总体持仓止盈基于当前平均持仓成本进行计算，触发条件满足时将平掉全部仓位</div>
        <a-alert 
          message="注意：所有批次平仓比例总和必须等于100%" 
          type="info" 
          show-icon 
          style="margin-top: 8px;"
        />
      </div>

      <a-table
        :dataSource="tempGlobalTakeProfitLevels"
        :columns="takeProfitLevelColumns"
        :pagination="false"
        :bordered="true"
        size="small"
      >
        <template #headerCell="{ column }">
          <template v-if="column.dataIndex === 'level'">
            <span>批次</span>
          </template>
          
          <template v-if="column.dataIndex === 'status'">
            <span>状态</span>
          </template>
          
          <template v-if="column.dataIndex === 'ratio'">
            <span>
              止盈比例(%)
              <a-tooltip placement="top">
                <template #title>达到该比例时触发止盈条件</template>
                <question-circle-outlined style="margin-left: 4px" />
              </a-tooltip>
            </span>
          </template>
          
          <template v-if="column.dataIndex === 'reboundRatio'">
            <span>
              回调比例(%)
              <a-tooltip placement="top">
                <template #title>价格从最高点回调多少比例时执行止盈</template>
                <question-circle-outlined style="margin-left: 4px" />
              </a-tooltip>
            </span>
          </template>
          
          <template v-if="column.dataIndex === 'portion'">
            <span>
              平仓比例
              <a-tooltip placement="top">
                <template #title>触发该止盈批次时平掉的仓位比例（所有批次比例总和为100%）</template>
                <question-circle-outlined style="margin-left: 4px" />
              </a-tooltip>
            </span>
          </template>
        </template>
        
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'level'">
            <span>{{ record.level }}</span>
          </template>
          
          <template v-if="column.dataIndex === 'status'">
            <a-tag :color="getTakeProfitStatusColor(record.status)">{{ record.status || '未触发' }}</a-tag>
          </template>
          
          <template v-if="column.dataIndex === 'ratio'">
            <a-input-number 
              v-model:value="record.ratio" 
              :precision="1" 
              :min="0.1" 
              :step="0.1" 
              style="width: 100%" 
            />
          </template>
          
          <template v-if="column.dataIndex === 'reboundRatio'">
            <a-input-number 
              v-model:value="record.reboundRatio" 
              :precision="1" 
              :min="0.1" 
              :step="0.1" 
              style="width: 100%" 
            />
          </template>
          
          <template v-if="column.dataIndex === 'portion'">
            <a-input-number 
              v-model:value="record.portion" 
              :precision="0" 
              :min="1" 
              :max="100" 
              :step="5" 
              @change="updateGlobalPortionDistribution"
              style="width: 100%" 
              :formatter="(value: number) => `${value}%`"
              :parser="(value: string) => value ? value.replace('%', '') : value"
            />
          </template>
          
          <template v-if="column.dataIndex === 'action'">
            <a-button 
              type="link" 
              danger 
              size="small" 
              @click="deleteGlobalTakeProfitLevel(record)"
            >
              删除
            </a-button>
          </template>
        </template>
      </a-table>

      <div class="total-portion" style="margin-top: 8px; text-align: right;">
        <a-tag v-if="calculateGlobalTotalPortion() !== 100" color="error">总平仓比例必须等于100%</a-tag>
      </div>

      <div style="margin-top: 16px;">
        <a-button type="dashed" block @click="addGlobalTakeProfitLevel">
          <template #icon><plus-outlined /></template>
          添加止盈批次
        </a-button>
      </div>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { message } from 'ant-design-vue';
import {
  PlusOutlined,
  DeleteOutlined,
  SettingOutlined,
  ArrowLeftOutlined,
  ArrowRightOutlined,
  QuestionCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons-vue';

const router = useRouter();
const route = useRoute();
const formRef = ref();

// 获取URL参数
const exchange = route.query.exchange as string;
const marketType = route.query.marketType as string;
const direction = route.query.direction as string;
const baseCurrency = route.query.baseCurrency as string;
const quoteCurrency = route.query.quoteCurrency as string;

// 止盈层级接口
interface TakeProfitLevel {
  key: number;
  level: number;
  ratio: number;  // 止盈比例
  reboundRatio: number;  // 回调比例
  portion: number;  // 平仓比例
  status?: string;  // 止盈状态
}

// 网格层级接口
interface GridLevel {
  key: number;
  level: number;
  openReboundRatio: number;
  openRatio: number;
  size: number;
  status: string;
  editable: boolean;
  takeProfitLevels: TakeProfitLevel[];
}

// 网格策略表单
const gridForm = reactive({
  gridCount: 5,
  investment: 100,
  takeProfitType: 'grid'
});

// 网格策略验证规则
const gridRules = {
  gridCount: [{ required: true, message: '请输入网格数量' }],
  investment: [{ required: true, message: '请输入投资张数' }]
};

// 网格层级数据
const gridLevels = ref<GridLevel[]>([]);

// 总体持仓止盈层级
const globalTakeProfitLevels = ref<TakeProfitLevel[]>([]);

// 网格层级列定义
const gridLevelColumns = [
  { title: '层级', dataIndex: 'level', key: 'level', width: 60, align: 'center' },
  { title: '状态', dataIndex: 'status', key: 'status', width: 80, align: 'center' },
  { title: '张数', dataIndex: 'size', key: 'size', width: 60, align: 'center' },
  { title: '开仓比例(%)', dataIndex: 'openRatio', key: 'openRatio', width: 130, align: 'center' },
  { title: '开仓反弹比例(%)', dataIndex: 'openReboundRatio', key: 'openReboundRatio', width: 150, align: 'center' },
  { title: '止盈', dataIndex: 'takeProfit', key: 'takeProfit', width: 100, align: 'center' },
  { title: '操作', dataIndex: 'action', key: 'action', width: 80, align: 'center' }
];

// 止盈层级列定义
const takeProfitLevelColumns = [
  { title: '批次', dataIndex: 'level', key: 'level', width: 60, align: 'center' },
  { title: '状态', dataIndex: 'status', key: 'status', width: 80, align: 'center' },
  { title: '止盈比例(%)', dataIndex: 'ratio', key: 'ratio', width: 120, align: 'center' },
  { title: '回调比例(%)', dataIndex: 'reboundRatio', key: 'reboundRatio', width: 120, align: 'center' },
  { title: '平仓比例', dataIndex: 'portion', key: 'portion', width: 100, align: 'center' },
  { title: '操作', dataIndex: 'action', key: 'action', width: 80, align: 'center' }
];

// 止盈弹窗相关
const takeProfitModalVisible = ref(false);
const globalTakeProfitModalVisible = ref(false);
const currentEditingGridLevel = ref<GridLevel | null>(null);
const tempTakeProfitLevels = ref<TakeProfitLevel[]>([]);
const tempGlobalTakeProfitLevels = ref<TakeProfitLevel[]>([]);

// 计算属性：全局止盈层级数量
const globalTakeProfitLength = computed(() => {
  return globalTakeProfitLevels.value?.length || 0;
});

// 计算属性：首个全局止盈批次的止盈比例
const firstGlobalTakeProfitRatio = computed(() => {
  return globalTakeProfitLevels.value?.[0]?.ratio || 0;
});

// 计算属性：首个全局止盈批次的平仓比例
const firstGlobalTakeProfitPortion = computed(() => {
  return globalTakeProfitLevels.value?.[0]?.portion || 0;
});

// 获取状态颜色
const getStatusColor = (status: string) => {
  switch (status) {
    case '已开仓': return 'error';
    case '待止盈': return 'success';
    case '待开仓': return 'processing';
    case '未开仓': return 'default';
    default: return 'default';
  }
};

// 检查是否有多层止盈
const hasMultipleTakeProfit = (record: GridLevel) => {
  return record.takeProfitLevels && record.takeProfitLevels.length > 1;
};

// 检查是否设置了总体止盈
const hasGlobalTakeProfit = () => {
  return globalTakeProfitLevels.value && globalTakeProfitLevels.value.length > 0;
};

// 生成网格层级
const generateGridLevels = () => {
  if (!gridForm.gridCount || gridForm.gridCount < 2) {
    return;
  }
  
  // 清空原有层级
  gridLevels.value = [];
  
  // 计算每个层级
  const levels: GridLevel[] = [];
  
  for (let i = 0; i < gridForm.gridCount; i++) {
    levels.push({
      key: i,
      level: i + 1,
      openReboundRatio: 0.5,
      openRatio: 1.0,
      size: Math.ceil(gridForm.investment / gridForm.gridCount),
      status: '未开仓',
      editable: true,
      takeProfitLevels: [
        {
          key: 0,
          level: 1,
          ratio: 1.0,
          reboundRatio: 0.5,
          portion: 100
        }
      ]
    });
  }
  
  gridLevels.value = levels;
};

// 删除网格层级
const deleteGridLevel = (record: GridLevel) => {
  const index = gridLevels.value.findIndex(item => item.key === record.key);
  if (index !== -1) {
    gridLevels.value.splice(index, 1);
    
    // 重新排序层级
    gridLevels.value.forEach((item, i) => {
      item.level = i + 1;
    });
  }
};

// 打开止盈设置弹窗
const openTakeProfitModal = (record: GridLevel) => {
  currentEditingGridLevel.value = record;
  tempTakeProfitLevels.value = JSON.parse(JSON.stringify(record.takeProfitLevels || []));
  
  // 如果没有止盈层级，添加一个默认层级
  if (tempTakeProfitLevels.value.length === 0) {
    addTakeProfitLevel();
  }
  
  takeProfitModalVisible.value = true;
};

// 打开全局止盈设置弹窗
const openGlobalTakeProfitModal = () => {
  tempGlobalTakeProfitLevels.value = JSON.parse(JSON.stringify(globalTakeProfitLevels.value || []));
  
  // 如果没有全局止盈层级，添加一个默认层级
  if (tempGlobalTakeProfitLevels.value.length === 0) {
    addGlobalTakeProfitLevel();
  }
  
  globalTakeProfitModalVisible.value = true;
};

// 获取止盈状态颜色
const getTakeProfitStatusColor = (status: string) => {
  switch (status) {
    case '已触发': return 'success';
    case '进行中': return 'processing';
    case '已完成': return 'cyan';
    default: return 'default';
  }
};

// 计算总平仓比例
const calculateTotalPortion = () => {
  return tempTakeProfitLevels.value.reduce((sum, level) => sum + level.portion, 0);
};

// 计算全局止盈总平仓比例
const calculateGlobalTotalPortion = () => {
  return tempGlobalTakeProfitLevels.value.reduce((sum, level) => sum + level.portion, 0);
};

// 更新平仓比例分配
const updatePortionDistribution = () => {
  const total = calculateTotalPortion();
  if (total !== 100 && tempTakeProfitLevels.value.length > 1) {
    // 如果总和不等于100%且有多个批次，调整最后一个批次使总和为100%
    const lastIndex = tempTakeProfitLevels.value.length - 1;
    const otherSum = tempTakeProfitLevels.value.slice(0, lastIndex).reduce((sum, level) => sum + level.portion, 0);
    const newLastPortion = 100 - otherSum;
    
    if (newLastPortion > 0) {
      tempTakeProfitLevels.value[lastIndex].portion = newLastPortion;
    }
  }
};

// 更新全局平仓比例分配
const updateGlobalPortionDistribution = () => {
  const total = calculateGlobalTotalPortion();
  if (total !== 100 && tempGlobalTakeProfitLevels.value.length > 1) {
    // 如果总和不等于100%且有多个批次，调整最后一个批次使总和为100%
    const lastIndex = tempGlobalTakeProfitLevels.value.length - 1;
    const otherSum = tempGlobalTakeProfitLevels.value.slice(0, lastIndex).reduce((sum, level) => sum + level.portion, 0);
    const newLastPortion = 100 - otherSum;
    
    if (newLastPortion > 0) {
      tempGlobalTakeProfitLevels.value[lastIndex].portion = newLastPortion;
    }
  }
};

// 添加止盈层级
const addTakeProfitLevel = () => {
  const newLevel = tempTakeProfitLevels.value.length + 1;
  
  // 如果已有止盈层级，确保新层级的止盈比例高于前一层级
  let ratio = 1.0;
  if (tempTakeProfitLevels.value.length > 0) {
    const lastLevel = tempTakeProfitLevels.value[tempTakeProfitLevels.value.length - 1];
    ratio = lastLevel.ratio + 0.5;
  }
  
  // 所有层级的平仓比例总和始终为100%
  const newLevelCount = tempTakeProfitLevels.value.length + 1;
  const portionPerLevel = Math.floor(100 / newLevelCount);
  
  // 更新所有现有层级的平仓比例
  for (let i = 0; i < tempTakeProfitLevels.value.length; i++) {
    tempTakeProfitLevels.value[i].portion = portionPerLevel;
  }
  
  // 添加新层级
  tempTakeProfitLevels.value.push({
    key: Date.now(), // 使用时间戳作为临时key
    level: newLevel,
    ratio: ratio,
    reboundRatio: 0.5,
    status: '未触发',
    portion: portionPerLevel + (100 - portionPerLevel * newLevelCount) // 确保总和为100%
  });
};

// 添加全局止盈层级
const addGlobalTakeProfitLevel = () => {
  const newLevel = tempGlobalTakeProfitLevels.value.length + 1;
  
  // 如果已有止盈层级，确保新层级的止盈比例高于前一层级
  let ratio = 1.0;
  if (tempGlobalTakeProfitLevels.value.length > 0) {
    const lastLevel = tempGlobalTakeProfitLevels.value[tempGlobalTakeProfitLevels.value.length - 1];
    ratio = lastLevel.ratio + 0.5;
  }
  
  // 所有层级的平仓比例总和始终为100%
  const newLevelCount = tempGlobalTakeProfitLevels.value.length + 1;
  const portionPerLevel = Math.floor(100 / newLevelCount);
  
  // 更新所有现有层级的平仓比例
  for (let i = 0; i < tempGlobalTakeProfitLevels.value.length; i++) {
    tempGlobalTakeProfitLevels.value[i].portion = portionPerLevel;
  }
  
  // 添加新层级
  tempGlobalTakeProfitLevels.value.push({
    key: Date.now(), // 使用时间戳作为临时key
    level: newLevel,
    ratio: ratio,
    reboundRatio: 0.5,
    status: '未触发',
    portion: portionPerLevel + (100 - portionPerLevel * newLevelCount) // 确保总和为100%
  });
};

// 删除止盈层级
const deleteTakeProfitLevel = (record: TakeProfitLevel) => {
  const index = tempTakeProfitLevels.value.findIndex(item => item.key === record.key);
  if (index !== -1) {
    tempTakeProfitLevels.value.splice(index, 1);
    
    // 重新排序层级
    tempTakeProfitLevels.value.forEach((item, i) => {
      item.level = i + 1;
    });
    
    // 重新分配平仓比例，确保总和为100%
    if (tempTakeProfitLevels.value.length > 0) {
      const portionPerLevel = Math.floor(100 / tempTakeProfitLevels.value.length);
      for (let i = 0; i < tempTakeProfitLevels.value.length - 1; i++) {
        tempTakeProfitLevels.value[i].portion = portionPerLevel;
      }
      // 最后一层级占剩余比例，确保总和为100%
      tempTakeProfitLevels.value[tempTakeProfitLevels.value.length - 1].portion = 
        100 - portionPerLevel * (tempTakeProfitLevels.value.length - 1);
    }
  }
};

// 删除全局止盈层级
const deleteGlobalTakeProfitLevel = (record: TakeProfitLevel) => {
  const index = tempGlobalTakeProfitLevels.value.findIndex(item => item.key === record.key);
  if (index !== -1) {
    tempGlobalTakeProfitLevels.value.splice(index, 1);
    
    // 重新排序层级
    tempGlobalTakeProfitLevels.value.forEach((item, i) => {
      item.level = i + 1;
    });
    
    // 重新分配平仓比例，确保总和为100%
    if (tempGlobalTakeProfitLevels.value.length > 0) {
      const portionPerLevel = Math.floor(100 / tempGlobalTakeProfitLevels.value.length);
      for (let i = 0; i < tempGlobalTakeProfitLevels.value.length - 1; i++) {
        tempGlobalTakeProfitLevels.value[i].portion = portionPerLevel;
      }
      // 最后一层级占剩余比例，确保总和为100%
      tempGlobalTakeProfitLevels.value[tempGlobalTakeProfitLevels.value.length - 1].portion = 
        100 - portionPerLevel * (tempGlobalTakeProfitLevels.value.length - 1);
    }
  }
};

// 保存止盈设置
const saveTakeProfitSettings = () => {
  if (currentEditingGridLevel.value) {
    // 验证止盈层级
    for (const level of tempTakeProfitLevels.value) {
      if (!level.ratio || !level.reboundRatio || !level.portion) {
        message.error('请完善止盈批次设置');
        return;
      }
    }
    
    // 验证平仓比例总和是否为100%
    if (calculateTotalPortion() !== 100) {
      message.error('所有批次的平仓比例之和必须为100%');
      return;
    }
    
    // 将临时数据保存到网格层级中
    const index = gridLevels.value.findIndex(item => item.key === currentEditingGridLevel.value!.key);
    if (index !== -1) {
      gridLevels.value[index].takeProfitLevels = JSON.parse(JSON.stringify(tempTakeProfitLevels.value));
    }
    
    takeProfitModalVisible.value = false;
    currentEditingGridLevel.value = null;
  }
};

// 保存全局止盈设置
const saveGlobalTakeProfitSettings = () => {
  // 验证止盈层级
  for (const level of tempGlobalTakeProfitLevels.value) {
    if (!level.ratio || !level.reboundRatio || !level.portion) {
      message.error('请完善止盈批次设置');
      return;
    }
  }
  
  // 验证平仓比例总和是否为100%
  const totalPortion = tempGlobalTakeProfitLevels.value.reduce((sum, level) => sum + level.portion, 0);
  if (totalPortion !== 100) {
    message.error('所有批次的平仓比例之和必须为100%');
    return;
  }
  
  // 将临时数据保存
  globalTakeProfitLevels.value = JSON.parse(JSON.stringify(tempGlobalTakeProfitLevels.value));
  
  globalTakeProfitModalVisible.value = false;
};

// 取消止盈设置
const cancelTakeProfitSettings = () => {
  takeProfitModalVisible.value = false;
  currentEditingGridLevel.value = null;
};

// 取消全局止盈设置
const cancelGlobalTakeProfitSettings = () => {
  globalTakeProfitModalVisible.value = false;
};

// 导航到其他步骤
const goToStep = (step: string) => {
  if (step === 'basic') {
    goBack();
  } else if (step === 'risk') {
    router.push({
      path: '/strategies/create/risk',
      query: {
        ...route.query
      }
    });
  } else if (step === 'finish') {
    router.push({
      path: '/strategies',
    });
  }
};

// 保存并前往下一步
const saveAndGoNext = async () => {
  try {
    await formRef.value.validate();
    
    // 保存策略或发送到后端的逻辑
    // ...
    
    // 成功后导航到风控配置页面
    router.push({
      path: '/strategies/create/risk',
      query: {
        ...route.query,
        gridConfig: JSON.stringify(gridForm),
        gridLevels: JSON.stringify(gridLevels.value),
        globalTakeProfit: JSON.stringify(globalTakeProfitLevels.value),
        isGridStrategy: 'true'
      }
    });
    
  } catch (error) {
    message.error('请完善表单信息');
  }
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

// 使用旧组件
const goToOldComponent = () => {
  router.push({
    path: `/strategies/create/grid`,
    query: {
      ...route.query,
      useOldComponent: 'true'
    }
  });
};

// 添加网格层级
const addGridLevel = () => {
  if (gridLevels.value.length > 0) {
    const lastLevel = gridLevels.value[gridLevels.value.length - 1];
    const newKey = gridLevels.value.length;
    
    gridLevels.value.push({
      key: newKey,
      level: newKey + 1,
      openReboundRatio: 0.5,
      openRatio: 1.0,
      size: lastLevel.size,
      status: '未开仓',
      editable: true,
      takeProfitLevels: [
        {
          key: 0,
          level: 1,
          ratio: 1.0,
          reboundRatio: 0.5,
          portion: 100
        }
      ]
    });
  }
};

// 查看交易记录
const viewTransactionRecords = (record: GridLevel) => {
  message.info(`查看层级 ${record.level} 的交易记录`);
  // 这里可以实现跳转到交易记录页面或打开交易记录弹窗的逻辑
};

// 获取最高止盈比例
const getMaxTakeProfitRatio = () => {
  if (!globalTakeProfitLevels.value || globalTakeProfitLevels.value.length === 0) {
    return 0;
  }
  return Math.max(...globalTakeProfitLevels.value.map((level: TakeProfitLevel) => level.ratio));
};

// 获取当前持仓层数
const getCurrentPositionLevels = () => {
  return gridLevels.value.filter(level => level.status === '已开仓' || level.status === '待止盈').length;
};

// 获取总持仓张数
const getTotalPositionSize = () => {
  return gridLevels.value
    .filter(level => level.status === '已开仓' || level.status === '待止盈')
    .reduce((sum, level) => sum + level.size, 0);
};

// 获取当前收益
const getCurrentProfit = () => {
  // 这里只是模拟数据，实际项目中可能需要通过API获取或计算
  return (Math.random() * 10).toFixed(2);
};

// 组件挂载时生成网格层级
onMounted(() => {
  // 生成初始网格层级
  generateGridLevels();
});
</script>

<style scoped>
.strategy-view {
  width: 100%;
  background-color: #f0f2f5;
}

.card-title {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.card-title h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  white-space: nowrap;
}

.clickable-step {
  cursor: pointer;
  color: #1890ff;
  transition: color 0.3s;
}

.clickable-step:hover {
  color: #40a9ff;
  text-decoration: underline;
}

.config-card {
  margin-bottom: 16px;
  transition: all 0.3s;
  border-radius: 8px;
  overflow: hidden;
}

.config-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
}

.tab-description {
  color: #666;
  margin-bottom: 16px;
}

.readonly-row {
  background-color: #f5f5f5;
}

:deep(.ant-form-item-label) {
  font-weight: 500;
}

.take-profit-form {
  padding: 16px 0;
}

.level-info {
  border-bottom: 1px dashed #f0f0f0;
  padding-bottom: 16px;
  margin-bottom: 16px;
}

.card-title-with-tooltip {
  display: flex;
  align-items: center;
}

.card-title-with-tooltip span {
  font-size: 16px;
  font-weight: 500;
}

.title-container {
  display: flex;
  align-items: center;
}

.title-container h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.stat-header {
  font-weight: 500;
  margin-bottom: 8px;
  font-size: 15px;
  color: #555;
}

.stat-card {
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 5px rgba(0,0,0,0.05);
  transition: all 0.3s;
  text-align: center;
  height: 100%;
}

.stat-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.stat-title {
  font-weight: 500;
  margin-bottom: 12px;
  color: #666;
  font-size: 14px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  line-height: 1.2;
}

.positive {
  color: #52c41a;
}

.negative {
  color: #ff4d4f;
}

.add-button {
  transition: all 0.3s;
}

.add-button:hover {
  background-color: #f5f5f5;
  border-color: #1890ff;
}

:deep(.ant-table-thead > tr > th) {
  background-color: #f0f5ff;
  color: #333;
  font-weight: 600;
}

:deep(.ant-table-tbody > tr.ant-table-row:hover > td) {
  background-color: #e6f7ff;
}

.form-actions {
  margin-top: 24px;
  text-align: center;
}

:deep(.ant-btn) {
  border-radius: 4px;
  transition: all 0.3s;
}

:deep(.ant-btn:hover) {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(24, 144, 255, 0.4);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(24, 144, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(24, 144, 255, 0);
  }
}

:deep(.ant-btn-primary) {
  animation: pulse 2s infinite;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
  margin: 16px 0 24px 0;
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

/* 添加卡片样式重置 */
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
</style> 