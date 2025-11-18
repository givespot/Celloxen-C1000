#!/bin/bash
# Fix the three-column layout to have equal heights
sed -i 's/<div className="lg:col-span-1">/<div className="lg:col-span-1 flex">/g' index.html
sed -i 's/bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition-all duration-300/bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 flex-1/g' index.html
