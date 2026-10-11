
% This script reproduces the behavioral and ERP analyses for the index patient 
% in the facial emotion discrimination task.

% It computes block-level behavioral metrics (fear-choice rate, reaction time, confidence), 
% and extracts happy vs. fearful L-ERPs for each SEEG channel.

% All analyses use the data structure indexPatient.mat containing SEEG signals, 
% event information, and channel locations.

% Tao Xie, 11/17/2025

clc,clear;
load('indexPatient.mat');

%% behaveral analysis
typ = {'pre','post'};
run = 1:4;
fearVal = [0 30 40 50 60 70 100];
rlt = struct; kk=0;
for indxTyp = 1:length(typ)
for indxRun = 1:length(run)
    locTyp = cellfun(@(x)strcmp(x,typ{indxTyp}),{eeg.event.session});
    locRun = [eeg.event.runNum]==run(indxRun);
    trial = eeg.event(locTyp&locRun);
    trial = trial([trial.validity]==1);
    if ~isempty(trial)
        kk = kk+1;
        rlt(kk).typ = typ{indxTyp};
        rlt(kk).runNum = run(indxRun);
        for i = 1:length(fearVal)
            loc = [trial.fear]==fearVal(i);
            % fear chose rate (%)
            rlt(kk).fchoRate(i,1) = sum([trial(loc).em]==37)/sum(loc)*100;
            % reaction time
            val = [trial(loc).emRT];
            rlt(kk).rt_mean(i,1) = mean(val);
            % confidence
            val = [trial(loc).cf]-37;
            rlt(kk).cf_mean(i,1) = mean(val);
        end
    end
end
end
    
figure; hold on;
col = [0 0 0; 0 0 0; 0 0 0; 1 0 0;  1 0 0;  1 0 0;  1 0 0; ];
markTyp = {'o','square','diamond','o','square','diamond','hexagram'};
ha = [];
for indx = 1:length(rlt)
    if indx<=3; s = -1.5; else; s = 1.5; end
     ha(indx) = plot(fearVal+s,rlt(indx).fchoRate,markTyp{indx},'markerfacecolor','none','markeredgecolor',col(indx,:),'markersize',15,'LineWidth',2);
     nam{indx} = [rlt(indx).typ 'Abl : block ' num2str(rlt(indx).runNum)];
end
grid on;
xlabel('Fear intensity level (%)'); ylabel('Percentage of faces judged as fearful (%)'); 
legend(ha,nam,'Location','northeastoutside');
set(gca,'fontsize',18,'xlim',[-5 105],'ylim',[-5 110],'xtick',fearVal,'ytick',0:20:100,'TickLength',[0.03 0.03]); 
saveas(gcf,'Behavioral_preVSpost','png')

%% ERP analysis
typ = {'pre','post'};
cat = {[0 30 40];[60 70 100]}; % happy/fearful
rlt = struct;
for ch = 1:eeg.nbchan
for indxTyp = 1:length(typ)
    for indxCat = 1:length(cat)
        locTyp = cellfun(@(x)strcmp(x,typ{indxTyp}),{eeg.event.session});
        locCat = false(1,length(locTyp));
        for i = 1:length(cat{indxCat})
            locCat = locCat | [eeg.event.fear]==cat{indxCat}(i);
        end
        dat = squeeze(eeg.data(ch,:,locTyp&locCat));
        rlt(ch).(typ{indxTyp})(indxCat,:) = mean(dat,2);
    end
end
end

% A sample channel in the left amygdala
figure;
ch = 2;
subplot(1,2,1); hold on;
datH = rlt(ch).pre(1,:);
datF = rlt(ch).pre(2,:);
plot(eeg.times,double(datH),'Color',[0 0 0],'LineWidth',3);
plot(eeg.times,double(datF),'Color',[0 1 0],'LineWidth',3);
% define the lab
if eeg.chanlocs(ch).tala(1)<0; lr='L'; else; lr='R'; end
lab = [lr ': ' eeg.chanlocs(ch).annotation{:}];
title(['PreAbl: ' lab]); ylim([-1.2 0.5]);  xlim([-200 800])
xlabel('Time (ms)'); ylabel('Evoked potentials (normalized)')
set(gca,'fontsize',14);

subplot(1,2,2); hold on;
datH = rlt(ch).post(1,:);
datF = rlt(ch).post(2,:);
ha = [];
ha(1) = plot(eeg.times,double(datH),'Color',[0 0 0],'LineWidth',3);
ha(2) = plot(eeg.times,double(datF),'Color',[0 1 0],'LineWidth',3);
% define the lab
if eeg.chanlocs(ch).tala(1)<0; lr='L'; else; lr='R'; end
lab = [lr ': ' eeg.chanlocs(ch).annotation{:}];
title(['PostAbl: ' lab]); ylim([-1.2 0.5]); xlim([-200 800])
xlabel('Time (ms)'); ylabel('Evoked potentials (normalized)')
legend(ha,{'Happy faces', 'Fearful faces'},'Location','northeast')
set(gca,'fontsize',14);
saveas(gcf,'exampleERP_preVSpost','png')


% all channel: pre Ablation
figure('Position',[10 10 2400 1200]);
tiledlayout(10,16, 'TileSpacing','compact', 'Padding','compact');
for ch = 1:eeg.nbchan
    ax = nexttile; hold on; 
    datH = rlt(ch).pre(1,:);
    datF = rlt(ch).pre(2,:);
    %figure;hold on;
    plot(eeg.times,double(datH),'Color',[0 0 0],'LineWidth',3);
    plot(eeg.times,double(datF),'Color',[0 1 0],'LineWidth',3);
    % define the lab
    if eeg.chanlocs(ch).tala(1)<0; lr='L'; else; lr='R'; end
    lab = [lr ': ' eeg.chanlocs(ch).annotation{:}];
    set(gca,'xtick',[],'ytick',[]);
    title(lab);
    ylim([-1 1])
end
saveas(gcf,'allERP_preAbl','png')

% all channel: post Ablation
figure('Position',[10 10 2400 1200]);
t = tiledlayout(10,16, 'TileSpacing','compact', 'Padding','compact');
ablatedChan = {'AR2','AR3','AR4','AR5','AR6'};
for ch = 1:eeg.nbchan
    ax = nexttile; hold on; 
    datH = rlt(ch).post(1,:);
    datF = rlt(ch).post(2,:);
    if sum(ismember(ablatedChan,eeg.chanlocs(ch).labels))==0
        %figure;hold on;
        plot(eeg.times,double(datH),'Color',[0 0 0],'LineWidth',3);
        plot(eeg.times,double(datF),'Color',[0 1 0],'LineWidth',3);
        % define the lab
        if eeg.chanlocs(ch).tala(1)<0; lr='L'; else; lr='R'; end
        lab = [lr ': ' eeg.chanlocs(ch).annotation{:}];
        set(gca,'xtick',[],'ytick',[]);
        title(lab);
        ylim([-1 1])
    end
end
saveas(gcf,'allERP_postAbl','png')

