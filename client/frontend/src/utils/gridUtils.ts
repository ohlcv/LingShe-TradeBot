/**
 * 网格策略相关工具函数
 */

/**
 * 网格等级接口
 */
export interface GridLevel {
    key: string;
    level: number;
    priceRange: string;
    openSpacing: number;
    reboundRatio: number;
    takeProfitRatio: number;
    takeProfitReboundRatio: number;
    size: number;
    status: string;
    enabled: boolean;
    editable: boolean;
}

/**
 * 梯度数据接口
 */
export interface GridLevelLadder {
    key: number;
    level: number;
    percentage: number;
    portion: number;
    editable: boolean;
}

/**
 * 验证结果接口
 */
export interface ValidationResult {
    valid: boolean;
    message: string;
}

/**
 * 生成网格层级数据
 * @param gridType 网格类型（算术或几何）
 * @param upperPrice 上限价格
 * @param lowerPrice 下限价格
 * @param gridCount 网格数量
 * @param currentPrice 当前价格
 * @returns 网格层级数据
 */
export function generateGridLevels(
    gridType: 'arithmetic' | 'geometric',
    upperPrice: number,
    lowerPrice: number,
    gridCount: number,
    currentPrice?: number
): GridLevel[] {
    // 网格价格验证
    if (upperPrice <= lowerPrice) {
        return [];
    }

    // 网格数量验证
    if (gridCount < 2) {
        return [];
    }

    const levels: GridLevel[] = [];
    const isArithmetic = gridType === 'arithmetic';

    // 计算网格间距
    let gridSpacing = 0;
    if (isArithmetic) {
        // 算术网格: 等差递增
        gridSpacing = (upperPrice - lowerPrice) / gridCount;
    } else {
        // 几何网格: 等比递增
        gridSpacing = Math.pow(upperPrice / lowerPrice, 1 / gridCount);
    }

    // 生成网格层级
    for (let i = 0; i <= gridCount; i++) {
        let price = 0;
        if (isArithmetic) {
            price = lowerPrice + i * gridSpacing;
        } else {
            price = lowerPrice * Math.pow(gridSpacing, i);
        }

        // 计算网格层的价格区间
        const lowerBound = i === 0 ? price : isArithmetic ? price - gridSpacing : price / gridSpacing;
        const upperBound = i === gridCount ? price : isArithmetic ? price + gridSpacing : price * gridSpacing;

        // 判断当前价格是否在网格层内
        const isCurrentPriceInLevel = currentPrice !== undefined &&
            currentPrice >= lowerBound && currentPrice <= upperBound;

        // 设置默认回撤比例和止盈比例
        const reboundRatio = i === 0 ? 0 : 0.5;
        const takeProfitRatio = i === gridCount ? 0 : 1.0;
        const takeProfitReboundRatio = 0.3;

        // 添加网格层级
        levels.push({
            key: `level-${i}`,
            level: i,
            priceRange: `${lowerBound.toFixed(2)} - ${upperBound.toFixed(2)}`,
            openSpacing: i === 0 || i === gridCount ? 0 : 1,
            reboundRatio: reboundRatio,
            takeProfitRatio: takeProfitRatio,
            takeProfitReboundRatio: takeProfitReboundRatio,
            size: 1,
            status: isCurrentPriceInLevel ? 'active' : 'inactive',
            enabled: i !== 0 && i !== gridCount,
            editable: true
        });
    }

    return levels;
}

/**
 * 判断当前价格是否在网格层级内
 * @param level 网格层级
 * @param currentPrice 当前价格
 * @returns 是否在内
 */
export function isCurrentPriceInLevel(level: GridLevel, currentPrice: number): boolean {
    // 从价格区间字符串解析出上下界
    const [lowerStr, upperStr] = level.priceRange.split(' - ');
    const lowerBound = parseFloat(lowerStr);
    const upperBound = parseFloat(upperStr);

    return currentPrice >= lowerBound && currentPrice <= upperBound;
}

/**
 * 验证梯度设置是否有效
 * @param ladders 梯度数据
 * @returns 验证结果
 */
export function validateGridLevelLadders(ladders: any[]): ValidationResult {
    // 验证梯度是否为空
    if (!ladders || ladders.length === 0) {
        return {
            valid: false,
            message: '梯度配置不能为空'
        };
    }

    // 验证梯度比例是否递增
    for (let i = 1; i < ladders.length; i++) {
        if (ladders[i].percentage <= ladders[i - 1].percentage) {
            return {
                valid: false,
                message: `第${i + 1}级止盈比例必须大于第${i}级`
            };
        }
    }

    // 计算总比例
    const totalPortion = ladders.reduce((sum, ladder) => sum + ladder.portion, 0);

    // 验证总比例是否为100%
    if (totalPortion !== 100) {
        return {
            valid: false,
            message: `仓位比例总和必须为100%，当前为${totalPortion}%`
        };
    }

    return {
        valid: true,
        message: '梯度设置有效'
    };
}

/**
 * 生成网格层级的梯度设置
 * @param levelCount 梯度级数
 * @returns 梯度数据
 */
export function generateGridLevelLadders(levelCount: number): GridLevelLadder[] {
    const ladders: GridLevelLadder[] = [];
    const defaultPortion = Math.floor(100 / levelCount);
    let remaining = 100;

    for (let i = 0; i < levelCount; i++) {
        let portion = i === levelCount - 1 ? remaining : defaultPortion;
        remaining -= portion;

        ladders.push({
            key: i,
            level: i + 1,
            percentage: 5 + i * 5, // 5%, 10%, 15%, ...
            portion: portion,
            editable: true
        });
    }

    return ladders;
}

/**
 * 生成利润梯度数据
 * @param levelCount 梯度级数
 * @returns 梯度数据
 */
export function generateProfitLadders(levelCount: number): GridLevelLadder[] {
    const ladders: GridLevelLadder[] = [];
    const defaultPortion = Math.floor(100 / levelCount);
    let remaining = 100;

    for (let i = 0; i < levelCount; i++) {
        let portion = i === levelCount - 1 ? remaining : defaultPortion;
        remaining -= portion;

        ladders.push({
            key: i,
            level: i + 1,
            percentage: 5 + i * 5, // 5%, 10%, 15%, ...
            portion: portion,
            editable: true
        });
    }

    return ladders;
} 