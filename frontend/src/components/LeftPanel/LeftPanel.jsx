import React from 'react';
import { FiSearch } from 'react-icons/fi';
import { AiFillFire } from 'react-icons/ai';
import { categories, priceChanges, sectors, mockCompanies } from '../../data/mockData';
import './LeftPanel.css';

const LeftPanel = () => {
  return (
    <div className="left-panel">
      {/* Поиск */}
      <div className="search-box">
        <FiSearch className="search-icon" />
        <input type="text" placeholder="Поиск" className="search-input" />
      </div>

      {/* Категории */}
      <div className="filter-section">
        {categories.map((category, index) => (
          <button key={index} className="filter-item">
            {category}
          </button>
        ))}
      </div>

      {/* Компании */}
      <div className="filter-section">
        <h3 className="section-title">Компании</h3>
        {mockCompanies.map((company, index) => (
          <div key={index} className="company-item">
            <span className="company-name">
              Сбер <span className="ticker">#{company.ticker}</span>
            </span>
            <span className="company-hotness">
              {company.hotness} <AiFillFire color="#FF6B35" />
            </span>
          </div>
        ))}
        <button className="show-all-btn">Смотреть все</button>
      </div>

      {/* Изменение цены */}
      <div className="filter-section">
        <h3 className="section-title">Изменение цены</h3>
        {priceChanges.map((item, index) => (
          <button key={index} className="filter-item">
            <span className="item-icon">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </div>

      {/* Сектор рынка */}
      <div className="filter-section">
        <h3 className="section-title">Сектор рынка</h3>
        {sectors.map((sector, index) => (
          <button key={index} className="filter-item">
            <span className="item-icon">{sector.icon}</span>
            {sector.label}
          </button>
        ))}
        <button className="show-all-btn">Смотреть все</button>
      </div>
    </div>
  );
};

export default LeftPanel;