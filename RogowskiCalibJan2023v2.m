% multiply voltage by 1000 bc Pearson coil is attenuated a lot
% 2V in dataset is 2 kA in real life

% BRog1
% accounting for attenuation
% voltage gain = 20log(Vout/Vin), so since we know the attenuation in dB
% we can go backwards to get Vout, which is our signal pre-attenuation
dB1 = 19.82; % attenuation in decibels for BRog1
carray1 = table2array(coil1);
atten1 = 10.^(dB1/20).*carray1(:,2);
chan1 = cat(2, carray1(:, 1), atten1);
% smoothing the data
smooth1 = smoothdata(chan1,'loess', 1000);
c1t = smooth1(:,1);
c1y = smooth1(:,2);

figure(1)
subplot(2,2,1);
% raw Rogowski and attenuated Pearson
plot(coil1, "Time", "Current")
hold on
plot(pearson1, "Time", "Current");
hold off
title("Raw Data");
legend("Rogowski", "Attenuated Pearson")
% Pearson has 19.82 dB attenuation and 100x sensitivity so the value we get
% off of it is 1000x smaller
% 1 A thru Pearson would show up as 1 mV on scope

pearsondB = 19.82;
parray1 = table2array(pearson1);
% accounting for Pearson attenuation and sensitivity
patten1 = 100*(10.^(pearsondB/20).*parray1(:,2));
p1 = cat(2, parray1(:, 1), patten1); % unattenuated Pearson

subplot(2,2,2);
% smoothed
plot(c1t, c1y, 'LineWidth', 2);
xlabel("Time");
ylabel("Current");
title("Smoothed Rogowski Data");

subplot(2,2,3);
% smoothed and integrated
plot(c1t, cumtrapz(c1t, c1y), 'LineWidth', 2);
hold on

% finding slope of pre-signal noise
index11 = 1; % first value in datafile
index12 = 13961; % where the actual signal starts

coeff = polyfit([c1t(index11) c1t(index12)], [c1y(index11) c1y(index12)], 1);
a = coeff(1); % slope of constant line
b = coeff(2); % y-intercept of constant line
hold on
noise = @(t) a*t + b; % noise is some constant line after integration

% smoothed, integrated, w constant slope due to noise subtracted
% explanation: after integrating the smoothed data, notice that the part of
% the signal before the trigger (where it's flat and should be 0) has a non
% zero slope. subtracting that constant slope from the entire waveform
% should yield a smoothed waveform that matches up w our Pearson data.
plot(c1t, cumtrapz(c1t, c1y - noise(c1t)), 'LineWidth', 2);
hold off
xlabel("Time");
ylabel("Current");
title("Smoothed and Integrated Rogowski Data");
legend("Integrated", "Noise Removed");

% corrected data on top of raw Pearson coil data
subplot(2,2,4);
R1 = -765500000; % Rogowski coil coefficient
% multiply R by attenuation factor
plot(c1t, cumtrapz(c1t, R1*(c1y - noise(c1t))), '-*','MarkerIndices',1:2500:length(c1t));
hold on
plot(p1(:, 1), p1(:, 2));
hold off
title("Corrected Rogowski and Raw Pearson Data");
subtitle("Rogowski Coefficient = " + abs(R1))
legend("Rogowski", "Pearson")

% BRog2
% accounting for attenuation
% voltage gain = 20log(Vout/Vin), so since we know the attenuation in dB
% we can go backwards to get Vout, which is our signal pre-attenuation
dB2 = 19.49; % attenuation in decibels for BRog1
carray2 = table2array(coil2);
atten2 = 10.^(dB1/20).*carray2(:,2);
chan2 = cat(2, carray2(:, 1), atten2);
% smoothing the data
smooth2 = smoothdata(chan2,'loess', 1000);
c2t = smooth2(:,1);
c2y = smooth2(:,2);

figure(2)
subplot(2,2,1);
% raw Rogowski and Pearson
plot(coil2, "Time", "Current")
hold on
plot(pearson2, "Time", "Current");
hold off
title("Raw Data");
legend("Rogowski", "Attenuated Pearson")

parray2 = table2array(pearson2);
% accounting for Pearson attenuation and sensitivity
patten2 = 100*(10.^(pearsondB/20).*parray2(:,2));
p2 = cat(2, parray2(:, 1), patten2); 

subplot(2,2,2);
% smoothed
plot(c2t, c2y);
xlabel("Time");
ylabel("Current");
title("Smoothed Rogowski Data");

subplot(2,2,3);
% smoothed and integrated
plot(c2t, cumtrapz(c2t, c2y));
hold on

% finding slope of pre-signal noise
index21 = 1; % first value in datafile
index22 = 13957; % where the actual signal starts

coeff = polyfit([c2t(index21) c2t(index22)], [c2y(index21) c2y(index22)], 1);
a = coeff(1); % slope of constant line
b = coeff(2); % y-intercept of constant line
hold on
syms t;
noise = @(t) a*t + b;

% smoothed, integrated, w constant slope due to noise subtracted
% explanation: after integrating the smoothed data, notice that the part of
% the signal before the trigger (where it's flat and should be 0) has a non
% zero slope. subtracting that constant slope from the entire waveform
% should yield a smoothed waveform that matches up w our Pearson data.
plot(c2t, cumtrapz(c2t, c2y - noise(c2t)));
hold off
xlabel("Time");
ylabel("Current");
title("Smoothed and Integrated Rogowski Data");
legend("Integrated", "Noise Removed");

% corrected data on top of raw Pearson coil data
subplot(2,2,4);
R2 = 820000000; % Rogowski coil coefficient
% multiply R by attenuation factor
plot(c2t, cumtrapz(c2t, R2*(c2y - noise(c2t))), '-*','MarkerIndices',1:2500:length(c2t));
hold on
plot(p2(:, 1), p2(:, 2));
hold off
title("Corrected Rogowski and Raw Pearson Data");
subtitle("Rogowski Coefficient = " + abs(R2))
legend("Rogowski", "Pearson")