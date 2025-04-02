<template>
  <div class="filter-options-manager">
    <a-card :bordered="false" title="筛选条件统一管理">
      <!-- 返回按钮移至标题处，使用标题插槽 -->
      <template #title>
        <div style="display: flex; align-items: center;">
          <a-button type="link" style="margin-right: 8px; padding: 0" @click="returnToStrategies">
            <ArrowLeftOutlined />
          </a-button>
          <span>筛选条件统一管理</span>
        </div>
      </template>
      
      <a-tabs>
        <!-- 交易所管理 -->
        <a-tab-pane key="exchanges" tab="交易所管理">
          <a-table :dataSource="exchanges" :columns="exchangeColumns" rowKey="value">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-tag :color="getStatusColor(record.status)">
                  {{ getStatusText(record.status) }}
                </a-tag>
              </template>
              <template v-if="column.key === 'action'">
                <a-space>
                  <a-button type="primary" size="small" @click="editExchange(record)">编辑</a-button>
                  <a-button 
                    type="primary" 
                    danger 
                    size="small" 
                    @click="removeExchange(record)"
                    :disabled="record.status === 'active'"
                  >
                    删除
                  </a-button>
                  <a-button
                    v-if="record.status !== 'active'"
                    type="primary"
                    size="small"
                    @click="setExchangeStatus(record.value, 'active')"
                  >
                    启用
                  </a-button>
                  <a-button
                    v-if="record.status === 'active'"
                    type="default"
                    size="small"
                    @click="setExchangeStatus(record.value, 'maintenance')"
                  >
                    维护
                  </a-button>
                </a-space>
              </template>
            </template>
          </a-table>
          <div class="actions">
            <a-button type="primary" @click="showAddExchangeModal">添加交易所</a-button>
          </div>
        </a-tab-pane>
        
        <!-- 产品类型管理 -->
        <a-tab-pane key="marketTypes" tab="产品类型管理">
          <a-table :dataSource="marketTypes" :columns="marketTypeColumns" rowKey="value">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-tag :color="record.status === 'active' ? 'green' : 'red'">
                  {{ record.status === 'active' ? '已启用' : '已禁用' }}
                </a-tag>
              </template>
              <template v-if="column.key === 'action'">
                <a-space>
                  <a-button type="primary" size="small" @click="editMarketType(record)">编辑</a-button>
                  <a-button 
                    type="primary" 
                    danger 
                    size="small" 
                    @click="removeMarketType(record)"
                    :disabled="record.status === 'active'"
                  >
                    删除
                  </a-button>
                  <a-button
                    v-if="record.status !== 'active'"
                    type="primary"
                    size="small"
                    @click="setMarketTypeStatus(record.value, 'active')"
                  >
                    启用
                  </a-button>
                  <a-button
                    v-if="record.status === 'active'"
                    type="default"
                    size="small"
                    @click="setMarketTypeStatus(record.value, 'unavailable')"
                  >
                    禁用
                  </a-button>
                </a-space>
              </template>
            </template>
          </a-table>
          <div class="actions">
            <a-button type="primary" @click="showAddMarketTypeModal">添加产品类型</a-button>
          </div>
        </a-tab-pane>
        
        <!-- 持仓方向管理 -->
        <a-tab-pane key="directions" tab="持仓方向管理">
          <a-table :dataSource="directions" :columns="directionColumns" rowKey="value">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-tag :color="record.status === 'active' ? 'green' : 'red'">
                  {{ record.status === 'active' ? '已启用' : '已禁用' }}
                </a-tag>
              </template>
              <template v-if="column.key === 'action'">
                <a-space>
                  <a-button type="primary" size="small" @click="editDirection(record)">编辑</a-button>
                  <a-button 
                    type="primary" 
                    danger 
                    size="small" 
                    @click="removeDirection(record)"
                    :disabled="record.status === 'active'"
                  >
                    删除
                  </a-button>
                  <a-button
                    v-if="record.status !== 'active'"
                    type="primary"
                    size="small"
                    @click="setDirectionStatus(record.value, 'active')"
                  >
                    启用
                  </a-button>
                  <a-button
                    v-if="record.status === 'active'"
                    type="default"
                    size="small"
                    @click="setDirectionStatus(record.value, 'unavailable')"
                  >
                    禁用
                  </a-button>
                </a-space>
              </template>
            </template>
          </a-table>
          <div class="actions">
            <a-button type="primary" @click="showAddDirectionModal">添加持仓方向</a-button>
          </div>
        </a-tab-pane>
      </a-tabs>
      
      <!-- 交易所添加/编辑模态框 -->
      <a-modal
        v-model:visible="exchangeModalVisible"
        :title="isEdit ? '编辑交易所' : '添加交易所'"
        @ok="handleExchangeModalOk"
        @cancel="closeExchangeModal"
        :okText="isEdit ? '保存' : '添加'"
        cancelText="取消"
      >
        <a-form
          :model="exchangeForm"
          :rules="exchangeRules"
          ref="exchangeFormRef"
          layout="vertical"
        >
          <a-form-item label="交易所标识" name="value">
            <a-input 
              v-model:value="exchangeForm.value"
              placeholder="请输入交易所标识"
              :disabled="isEdit"
            />
          </a-form-item>
          
          <a-form-item label="交易所名称" name="label">
            <a-input 
              v-model:value="exchangeForm.label"
              placeholder="请输入交易所名称"
            />
          </a-form-item>
          
          <a-form-item label="交易所状态" name="status">
            <a-select v-model:value="exchangeForm.status">
              <a-select-option value="active">已启用</a-select-option>
              <a-select-option value="maintenance">维护中</a-select-option>
              <a-select-option value="unavailable">已禁用</a-select-option>
            </a-select>
          </a-form-item>
        </a-form>
      </a-modal>
      
      <!-- 产品类型添加/编辑模态框 -->
      <a-modal
        v-model:visible="marketTypeModalVisible"
        :title="isEdit ? '编辑产品类型' : '添加产品类型'"
        @ok="handleMarketTypeModalOk"
        @cancel="closeMarketTypeModal"
        :okText="isEdit ? '保存' : '添加'"
        cancelText="取消"
      >
        <a-form
          :model="marketTypeForm"
          :rules="marketTypeRules"
          ref="marketTypeFormRef"
          layout="vertical"
        >
          <a-form-item label="产品类型标识" name="value">
            <a-input 
              v-model:value="marketTypeForm.value"
              placeholder="请输入产品类型标识"
              :disabled="isEdit"
            />
          </a-form-item>
          
          <a-form-item label="产品类型名称" name="label">
            <a-input 
              v-model:value="marketTypeForm.label"
              placeholder="请输入产品类型名称"
            />
          </a-form-item>
          
          <a-form-item label="产品类型状态" name="status">
            <a-select v-model:value="marketTypeForm.status">
              <a-select-option value="active">已启用</a-select-option>
              <a-select-option value="unavailable">已禁用</a-select-option>
            </a-select>
          </a-form-item>
        </a-form>
      </a-modal>
      
      <!-- 持仓方向添加/编辑模态框 -->
      <a-modal
        v-model:visible="directionModalVisible"
        :title="isEdit ? '编辑持仓方向' : '添加持仓方向'"
        @ok="handleDirectionModalOk"
        @cancel="closeDirectionModal"
        :okText="isEdit ? '保存' : '添加'"
        cancelText="取消"
      >
        <a-form
          :model="directionForm"
          :rules="directionRules"
          ref="directionFormRef"
          layout="vertical"
        >
          <a-form-item label="持仓方向标识" name="value">
            <a-input 
              v-model:value="directionForm.value"
              placeholder="请输入持仓方向标识"
              :disabled="isEdit"
            />
          </a-form-item>
          
          <a-form-item label="持仓方向名称" name="label">
            <a-input 
              v-model:value="directionForm.label"
              placeholder="请输入持仓方向名称"
            />
          </a-form-item>
          
          <a-form-item label="持仓方向状态" name="status">
            <a-select v-model:value="directionForm.status">
              <a-select-option value="active">已启用</a-select-option>
              <a-select-option value="unavailable">已禁用</a-select-option>
            </a-select>
          </a-form-item>
        </a-form>
      </a-modal>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { message } from 'ant-design-vue';
import { useRouter } from 'vue-router';
import { useExchangeStore, Exchange } from '../../store/modules/exchange';
import { useMarketTypeStore, MarketType } from '../../store/modules/marketType';
import { useDirectionStore, Direction } from '../../store/modules/direction';
import { ArrowLeftOutlined } from '@ant-design/icons-vue';

const router = useRouter();

const exchangeStore = useExchangeStore();
const marketTypeStore = useMarketTypeStore();
const directionStore = useDirectionStore();

// 公共状态
const isEdit = ref(false);
const currentEditValue = ref('');

// ===== 交易所管理 =====
const exchangeFormRef = ref();
const exchangeModalVisible = ref(false);

// 交易所表格列定义
const exchangeColumns = [
  {
    title: '交易所标识',
    dataIndex: 'value',
    key: 'value',
  },
  {
    title: '交易所名称',
    dataIndex: 'label',
    key: 'label',
  },
  {
    title: '状态',
    key: 'status',
  },
  {
    title: '操作',
    key: 'action',
  },
];

// 交易所数据
const exchanges = computed(() => exchangeStore.getAllExchanges);

// 交易所表单数据
const exchangeForm = reactive({
  value: '',
  label: '',
  status: 'active' as 'active' | 'maintenance' | 'unavailable',
});

// 交易所表单验证规则
const exchangeRules = {
  value: [{ required: true, message: '请输入交易所标识' }],
  label: [{ required: true, message: '请输入交易所名称' }],
  status: [{ required: true, message: '请选择交易所状态' }],
};

// 状态颜色
const getStatusColor = (status: string | undefined) => {
  switch (status) {
    case 'active': return 'green';
    case 'maintenance': return 'orange';
    case 'unavailable': return 'red';
    default: return 'default';
  }
};

// 状态文本
const getStatusText = (status: string | undefined) => {
  switch (status) {
    case 'active': return '已启用';
    case 'maintenance': return '维护中';
    case 'unavailable': return '已禁用';
    default: return '未知';
  }
};

// 添加交易所
const showAddExchangeModal = () => {
  isEdit.value = false;
  exchangeForm.value = '';
  exchangeForm.label = '';
  exchangeForm.status = 'active';
  exchangeModalVisible.value = true;
};

// 编辑交易所
const editExchange = (record: Exchange) => {
  isEdit.value = true;
  currentEditValue.value = record.value;
  
  exchangeForm.value = record.value;
  exchangeForm.label = record.label;
  exchangeForm.status = record.status || 'active';
  
  exchangeModalVisible.value = true;
};

// 处理交易所模态框确认
const handleExchangeModalOk = async () => {
  try {
    await exchangeFormRef.value.validate();
    
    const exchange: Exchange = {
      value: exchangeForm.value,
      label: exchangeForm.label,
      status: exchangeForm.status
    };
    
    if (isEdit.value) {
      // 更新交易所
      exchangeStore.updateExchange(currentEditValue.value, exchange);
      message.success('交易所更新成功');
    } else {
      // 添加新交易所
      exchangeStore.addExchange(exchange);
      message.success('交易所添加成功');
    }
    
    closeExchangeModal();
  } catch (error) {
    console.error('验证失败:', error);
  }
};

// 关闭交易所模态框
const closeExchangeModal = () => {
  exchangeModalVisible.value = false;
};

// 删除交易所
const removeExchange = (record: Exchange) => {
  if (record.status === 'active') {
    message.warning('启用状态的交易所不能删除，请先禁用');
    return;
  }
  exchangeStore.removeExchange(record.value);
  message.success(`${record.label}已删除`);
};

// 设置交易所状态
const setExchangeStatus = (value: string, status: 'active' | 'maintenance' | 'unavailable') => {
  exchangeStore.setExchangeStatus(value, status);
  message.success(`交易所状态已更新为${getStatusText(status)}`);
};

// ===== 产品类型管理 =====
const marketTypeFormRef = ref();
const marketTypeModalVisible = ref(false);

// 产品类型表格列定义
const marketTypeColumns = [
  {
    title: '产品类型标识',
    dataIndex: 'value',
    key: 'value',
  },
  {
    title: '产品类型名称',
    dataIndex: 'label',
    key: 'label',
  },
  {
    title: '状态',
    key: 'status',
  },
  {
    title: '操作',
    key: 'action',
  },
];

// 产品类型数据
const marketTypes = computed(() => marketTypeStore.getAllMarketTypes);

// 产品类型表单数据
const marketTypeForm = reactive({
  value: '',
  label: '',
  status: 'active' as 'active' | 'unavailable',
});

// 产品类型表单验证规则
const marketTypeRules = {
  value: [{ required: true, message: '请输入产品类型标识' }],
  label: [{ required: true, message: '请输入产品类型名称' }],
  status: [{ required: true, message: '请选择产品类型状态' }],
};

// 添加产品类型
const showAddMarketTypeModal = () => {
  isEdit.value = false;
  marketTypeForm.value = '';
  marketTypeForm.label = '';
  marketTypeForm.status = 'active';
  marketTypeModalVisible.value = true;
};

// 编辑产品类型
const editMarketType = (record: MarketType) => {
  isEdit.value = true;
  currentEditValue.value = record.value;
  
  marketTypeForm.value = record.value;
  marketTypeForm.label = record.label;
  marketTypeForm.status = record.status || 'active';
  
  marketTypeModalVisible.value = true;
};

// 处理产品类型模态框确认
const handleMarketTypeModalOk = async () => {
  try {
    await marketTypeFormRef.value.validate();
    
    const marketType: MarketType = {
      value: marketTypeForm.value,
      label: marketTypeForm.label,
      status: marketTypeForm.status
    };
    
    if (isEdit.value) {
      // 更新产品类型
      marketTypeStore.updateMarketType(currentEditValue.value, marketType);
      message.success('产品类型更新成功');
    } else {
      // 添加新产品类型
      marketTypeStore.addMarketType(marketType);
      message.success('产品类型添加成功');
    }
    
    closeMarketTypeModal();
  } catch (error) {
    console.error('验证失败:', error);
  }
};

// 关闭产品类型模态框
const closeMarketTypeModal = () => {
  marketTypeModalVisible.value = false;
};

// 删除产品类型
const removeMarketType = (record: MarketType) => {
  if (record.status === 'active') {
    message.warning('启用状态的产品类型不能删除，请先禁用');
    return;
  }
  marketTypeStore.removeMarketType(record.value);
  message.success(`${record.label}已删除`);
};

// 设置产品类型状态
const setMarketTypeStatus = (value: string, status: 'active' | 'unavailable') => {
  marketTypeStore.setMarketTypeStatus(value, status);
  message.success(`产品类型状态已更新为${status === 'active' ? '已启用' : '已禁用'}`);
};

// ===== 持仓方向管理 =====
const directionFormRef = ref();
const directionModalVisible = ref(false);

// 持仓方向表格列定义
const directionColumns = [
  {
    title: '持仓方向标识',
    dataIndex: 'value',
    key: 'value',
  },
  {
    title: '持仓方向名称',
    dataIndex: 'label',
    key: 'label',
  },
  {
    title: '状态',
    key: 'status',
  },
  {
    title: '操作',
    key: 'action',
  },
];

// 持仓方向数据
const directions = computed(() => directionStore.getAllDirections);

// 持仓方向表单数据
const directionForm = reactive({
  value: '',
  label: '',
  status: 'active' as 'active' | 'unavailable',
});

// 持仓方向表单验证规则
const directionRules = {
  value: [{ required: true, message: '请输入持仓方向标识' }],
  label: [{ required: true, message: '请输入持仓方向名称' }],
  status: [{ required: true, message: '请选择持仓方向状态' }],
};

// 添加持仓方向
const showAddDirectionModal = () => {
  isEdit.value = false;
  directionForm.value = '';
  directionForm.label = '';
  directionForm.status = 'active';
  directionModalVisible.value = true;
};

// 编辑持仓方向
const editDirection = (record: Direction) => {
  isEdit.value = true;
  currentEditValue.value = record.value;
  
  directionForm.value = record.value;
  directionForm.label = record.label;
  directionForm.status = record.status || 'active';
  
  directionModalVisible.value = true;
};

// 处理持仓方向模态框确认
const handleDirectionModalOk = async () => {
  try {
    await directionFormRef.value.validate();
    
    const direction: Direction = {
      value: directionForm.value,
      label: directionForm.label,
      status: directionForm.status
    };
    
    if (isEdit.value) {
      // 更新持仓方向
      directionStore.updateDirection(currentEditValue.value, direction);
      message.success('持仓方向更新成功');
    } else {
      // 添加新持仓方向
      directionStore.addDirection(direction);
      message.success('持仓方向添加成功');
    }
    
    closeDirectionModal();
  } catch (error) {
    console.error('验证失败:', error);
  }
};

// 关闭持仓方向模态框
const closeDirectionModal = () => {
  directionModalVisible.value = false;
};

// 删除持仓方向
const removeDirection = (record: Direction) => {
  if (record.status === 'active') {
    message.warning('启用状态的持仓方向不能删除，请先禁用');
    return;
  }
  directionStore.removeDirection(record.value);
  message.success(`${record.label}已删除`);
};

// 设置持仓方向状态
const setDirectionStatus = (value: string, status: 'active' | 'unavailable') => {
  directionStore.setDirectionStatus(value, status);
  message.success(`持仓方向状态已更新为${status === 'active' ? '已启用' : '已禁用'}`);
};

// 返回策略列表
const returnToStrategies = () => {
  router.push('/strategies');
};
</script>

<style scoped>
.filter-options-manager {
  padding: 24px;
}

.actions {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style> 