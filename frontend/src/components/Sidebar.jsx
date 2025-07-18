import React from 'react';
import {
  TrendingUp, Zap, Users, ClipboardList, Lightbulb, Settings,
} from 'lucide-react';

const SidebarItem = ({ icon, text, active = false }) => {
  const baseStyle = "flex items-center space-x-3 rounded-lg px-4 py-2.5 transition-colors duration-200 font-medium text-sm";
  const activeStyle = "bg-[#E7F1F8] text-[#166A95]";
  const inactiveStyle = "text-gray-600 hover:bg-gray-100 hover:text-gray-900";

  return (
    <a href="#" className={`${baseStyle} ${active ? activeStyle : inactiveStyle}`}>
      {icon}
      <span>{text}</span>
    </a>
  );
};

const Sidebar = () => {
  return (
    // --- THE RESPONSIVE FIX IS HERE ---
    // 'hidden' -> Hides the sidebar by default.
    // 'md:flex' -> Displays it as a flex container on medium screens (>=768px) and up.
    <div className="hidden md:flex w-64 bg-white h-screen flex-col justify-between border-r border-gray-200">
      <div>
        <div className="px-6 py-8">
          <h1 className="leading-none">
            <span className="block text-3xl font-bold text-[#189B4B]">TRIM</span>
            <div className="flex items-baseline mt-1">
              <span className="text-lg font-semibold text-[#166A95] relative -top-2 mr-0.5">MP</span>
              <span className="text-3xl font-bold">
                <span className="text-[#189B4B]">EN</span>
                <span className="text-[#166A95]">SYSTEMS</span>
              </span>
            </div>
          </h1>
        </div>

        <nav className="flex flex-col space-y-1 px-4">
          <SidebarItem icon={<TrendingUp size={20} />} text="Data" active={true} />
          <SidebarItem icon={<Zap size={20} />} text="Library" />
          <SidebarItem icon={<Users size={20} />} text="People" />
          <SidebarItem icon={<ClipboardList size={20} />} text="Activities" />
          <div className="pt-6 pb-2 px-4">
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Support</h2>
          </div>
          <SidebarItem icon={<Lightbulb size={20} />} text="Get Started" />
          <SidebarItem icon={<Settings size={20} />} text="Settings" />
        </nav>
      </div>

      <div className="px-6 py-4 border-t border-gray-200">
        <p className="text-sm font-semibold text-gray-800">Developer</p>
        <p className="text-xs text-gray-500">developer@mpensystems.com</p>
      </div>
    </div>
  );
};

export default Sidebar;