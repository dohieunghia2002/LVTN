import { defineStore } from 'pinia';

export const useDishesStore = defineStore('dishes', {
  state: () => {
    return {
      ingredients: ['bánh đa', 'bánh hỏi', 'bì', 'bún', 'cá', 'chả cốm', 'chả giò', 'cơm', 'đậu hủ', 'dồi sụn',
        'dưa chua', 'gan', 'hủ tiếu', 'mì', 'mực', 'phở', 'rau răm', 'sườn', 'thịt băm', 'thịt bò', 'thịt gà',
        'thịt heo', 'thịt heo quay', 'tôm', 'tôm tít', 'trứng', 'viên mọc'],
      dishesName: ["Bún cá", "Hủ tiếu Mỹ Tho", "Bún nước lèo", "Cơm tấm Long Xuyên",
        "Bún hải sản bề bề", "Bánh hỏi heo quay", "Cơm gà", "Cao lầu", "Mì Quảng", "Bún bò Huế", "Phở Hà Nội",
        "Bún mực", "Bún mọc", "Bún đậu mắm tôm"]
    }
  }
})